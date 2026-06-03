# Senhas geradas aleatoriamente e armazenadas em Secrets Manager.
# JAMAIS chega ao tfstate em texto claro (só os outputs sensíveis ficam marcados;
# o tfstate em si DEVE viver em um S3 backend, NUNCA em git).

resource "random_password" "db_master" {
  length  = 32
  special = true
  # Caracteres seguros pra MySQL (sem '/', '@', '"', ' ', etc.)
  override_special = "!#$%&*+-=?^_~"
}

resource "random_password" "jwt" {
  length  = 64
  special = false # JWT secret é tratado como bytes; base62 é suficiente
}

resource "aws_secretsmanager_secret" "db_password" {
  name        = "${local.name}/db-password"
  description = "Senha do usuário master do RDS MySQL"
  # Para um showcase temporário, força exclusão imediata ao destruir.
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.db_master.result
}

resource "aws_secretsmanager_secret" "jwt" {
  name                    = "${local.name}/jwt-secret"
  description             = "Chave de assinatura do JWT da aplicação"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "jwt" {
  secret_id     = aws_secretsmanager_secret.jwt.id
  secret_string = random_password.jwt.result
}
