# ─── IAM ──────────────────────────────────────────────────────────────────────
# Access role: App Runner usa para puxar a imagem do ECR.
data "aws_iam_policy_document" "build_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["build.apprunner.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "apprunner_access" {
  name               = "${local.name}-apprunner-access"
  assume_role_policy = data.aws_iam_policy_document.build_assume.json
}

resource "aws_iam_role_policy_attachment" "apprunner_access_ecr" {
  role       = aws_iam_role.apprunner_access.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

# Instance role: App Runner usa para ler Secrets Manager em runtime.
data "aws_iam_policy_document" "tasks_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["tasks.apprunner.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "apprunner_instance" {
  name               = "${local.name}-apprunner-instance"
  assume_role_policy = data.aws_iam_policy_document.tasks_assume.json
}

data "aws_iam_policy_document" "read_secrets" {
  statement {
    actions = ["secretsmanager:GetSecretValue"]
    resources = [
      aws_secretsmanager_secret.db_password.arn,
      aws_secretsmanager_secret.jwt.arn,
    ]
  }
}

resource "aws_iam_role_policy" "read_secrets" {
  role   = aws_iam_role.apprunner_instance.id
  policy = data.aws_iam_policy_document.read_secrets.json
}

# ─── Auto Scaling: 1 instância única, sem scale-out ──────────────────────────
# Projeto de showcase quase nunca terá 5 requisições simultâneas. Travamos em
# 1 instância (sem scale-out) e teto baixo de concorrência — qualquer cenário
# anômalo simplesmente enfileira em vez de virar uma conta cara.
resource "aws_apprunner_auto_scaling_configuration_version" "this" {
  auto_scaling_configuration_name = "${local.name}-asc"
  max_concurrency                 = 25
  min_size                        = 1
  max_size                        = 1
}

# ─── VPC Connector + Service ──────────────────────────────────────────────────
resource "aws_apprunner_vpc_connector" "this" {
  vpc_connector_name = "${local.name}-vpc-connector"
  subnets            = aws_subnet.private[*].id
  security_groups    = [aws_security_group.apprunner.id]
}

resource "aws_apprunner_service" "this" {
  service_name = local.name

  auto_scaling_configuration_arn = aws_apprunner_auto_scaling_configuration_version.this.arn

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_access.arn
    }

    image_repository {
      image_identifier      = "${aws_ecr_repository.this.repository_url}:${var.container_image_tag}"
      image_repository_type = "ECR"

      image_configuration {
        port = "3000"

        runtime_environment_variables = {
          NODE_ENV     = "production"
          PORT         = "3000"
          DB_HOST      = aws_db_instance.this.address
          DB_PORT      = "3306"
          DB_USER      = "dbadmin"
          DB_NAME      = "gymcontrol"
          AUTO_MIGRATE = "1"
          CORS_ORIGINS = var.frontend_origin
        }

        runtime_environment_secrets = {
          DB_PASSWORD = aws_secretsmanager_secret.db_password.arn
          JWT_SECRET  = aws_secretsmanager_secret.jwt.arn
        }
      }
    }

    auto_deployments_enabled = false
  }

  instance_configuration {
    cpu               = var.apprunner_cpu
    memory            = var.apprunner_memory
    instance_role_arn = aws_iam_role.apprunner_instance.arn
  }

  network_configuration {
    egress_configuration {
      egress_type       = "VPC"
      vpc_connector_arn = aws_apprunner_vpc_connector.this.arn
    }
    ingress_configuration {
      is_publicly_accessible = true
    }
  }

  health_check_configuration {
    protocol            = "HTTP"
    path                = "/healthz"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 1
    unhealthy_threshold = 5
  }

  # Garante que o RDS esteja "available" antes do AppRunner subir.
  depends_on = [aws_db_instance.this]
}
