resource "aws_db_subnet_group" "this" {
  name       = "${local.name}-db-subnets"
  subnet_ids = aws_subnet.private[*].id

  tags = { Name = "${local.name}-db-subnets" }
}

resource "aws_db_parameter_group" "this" {
  name        = "${local.name}-mysql8"
  family      = "mysql8.0"
  description = "Parâmetros utf8mb4 + slow log mínimo"

  parameter {
    name  = "character_set_server"
    value = "utf8mb4"
  }
  parameter {
    name  = "collation_server"
    value = "utf8mb4_unicode_ci"
  }
}

resource "aws_db_instance" "this" {
  identifier        = "${local.name}-mysql"
  engine            = "mysql"
  engine_version    = "8.0"
  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage_gb
  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = "gymcontrol"
  username = "dbadmin"
  password = random_password.db_master.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.this.name
  parameter_group_name   = aws_db_parameter_group.this.name

  publicly_accessible      = false
  multi_az                 = false
  backup_retention_period  = var.db_backup_retention_days
  delete_automated_backups = true
  deletion_protection      = false
  skip_final_snapshot      = true
  apply_immediately        = true

  # Free-tier para t4g.micro nos primeiros 12 meses.
  performance_insights_enabled = false
  monitoring_interval          = 0
  copy_tags_to_snapshot        = true

  tags = { Name = "${local.name}-mysql" }
}
