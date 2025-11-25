# Main Terraform configuration file

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Terraform   = "true"
  }
}

# Random password for RDS
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Store DB credentials in Secrets Manager
resource "aws_secretsmanager_secret" "rds_credentials" {
  name                    = "${local.name_prefix}-rds-credentials"
  description             = "Aurora PostgreSQL credentials for document querying system"
  recovery_window_in_days = 7
  
  tags = local.common_tags
}

# Budget-friendly RDS PostgreSQL
resource "aws_db_instance" "postgres_budget" {
  identifier = "${local.name_prefix}-postgres"
  
  engine         = "postgres"
  # engine_version will use latest supported version
  instance_class = "db.t3.micro"
  
  allocated_storage = 20
  storage_type     = "gp2"
  storage_encrypted = true
  
  db_name  = var.database_name
  username = var.db_master_username
  password = random_password.db_password.result
  
  vpc_security_group_ids = [aws_security_group.aurora.id]
  db_subnet_group_name   = aws_db_subnet_group.public.name
  
  backup_retention_period = 1
  skip_final_snapshot    = true
  deletion_protection    = false
  publicly_accessible    = true
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "rds_credentials" {
  secret_id = aws_secretsmanager_secret.rds_credentials.id
  secret_string = jsonencode({
    username = var.db_master_username
    password = random_password.db_password.result
    engine   = "postgres"
    host     = aws_db_instance.postgres_budget.endpoint
    port     = 5432
    dbname   = var.database_name
  })
}
