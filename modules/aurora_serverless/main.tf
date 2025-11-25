# Aurora Serverless Module
data "aws_caller_identity" "current" {}

# Random password for RDS
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Store DB credentials in Secrets Manager
resource "aws_secretsmanager_secret" "rds_credentials" {
  name                    = "${var.name_prefix}-rds-credentials"
  description             = "Aurora PostgreSQL credentials for document querying system"
  recovery_window_in_days = 7
  
  tags = var.common_tags
}

resource "aws_secretsmanager_secret_version" "rds_credentials" {
  secret_id = aws_secretsmanager_secret.rds_credentials.id
  secret_string = jsonencode({
    username = var.db_master_username
    password = random_password.db_password.result
    engine   = "postgres"
    host     = aws_rds_cluster.aurora_cluster.endpoint
    port     = 5432
    dbname   = var.database_name
  })
}

# Aurora PostgreSQL Serverless Cluster
resource "aws_rds_cluster" "aurora_cluster" {
  cluster_identifier      = "${var.name_prefix}-cluster"
  engine                  = "aurora-postgresql"
  engine_mode             = "provisioned"
  database_name           = var.database_name
  master_username         = var.db_master_username
  master_password         = random_password.db_password.result
  
  db_subnet_group_name    = aws_db_subnet_group.aurora.name
  vpc_security_group_ids  = [aws_security_group.aurora.id]
  
  backup_retention_period = 1
  preferred_backup_window = "03:00-04:00"
  
  skip_final_snapshot     = true
  apply_immediately       = true
  enable_http_endpoint    = true
  
  serverlessv2_scaling_configuration {
    max_capacity = 1.0
    min_capacity = 0.5
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-aurora-cluster"
  })
}

# Aurora Cluster Instance
resource "aws_rds_cluster_instance" "aurora_instance" {
  identifier          = "${var.name_prefix}-instance"
  cluster_identifier  = aws_rds_cluster.aurora_cluster.id
  instance_class      = "db.serverless"
  engine              = aws_rds_cluster.aurora_cluster.engine
  engine_version      = aws_rds_cluster.aurora_cluster.engine_version
  
  publicly_accessible = false
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-aurora-instance"
  })
}

# DB Subnet Group
resource "aws_db_subnet_group" "aurora" {
  name       = "${var.name_prefix}-db-subnet-group"
  subnet_ids = var.private_subnet_ids
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-db-subnet-group"
  })
}

# Security Group for Aurora
resource "aws_security_group" "aurora" {
  name        = "${var.name_prefix}-aurora-sg"
  description = "Security group for Aurora PostgreSQL cluster"
  vpc_id      = var.vpc_id
  
  ingress {
    description = "PostgreSQL from VPC"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-aurora-sg"
  })
}