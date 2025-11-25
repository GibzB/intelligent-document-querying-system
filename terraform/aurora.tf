# Aurora PostgreSQL Serverless Cluster - Required for Bedrock Knowledge Base
resource "aws_rds_cluster" "aurora_cluster" {
  cluster_identifier      = "${local.name_prefix}-cluster"
  engine                  = "aurora-postgresql"
  engine_mode             = "provisioned"
  database_name           = var.database_name
  master_username         = var.db_master_username
  master_password         = random_password.db_password.result
  
  db_subnet_group_name    = aws_db_subnet_group.public.name
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
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-aurora-cluster"
  })
}

# Aurora Cluster Instance - Required for Bedrock Knowledge Base
resource "aws_rds_cluster_instance" "aurora_instance" {
  identifier          = "${local.name_prefix}-instance"
  cluster_identifier  = aws_rds_cluster.aurora_cluster.id
  instance_class      = "db.serverless"
  engine              = aws_rds_cluster.aurora_cluster.engine
  engine_version      = aws_rds_cluster.aurora_cluster.engine_version
  
  publicly_accessible = false
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-aurora-instance"
  })
}

# DB Subnet Group - Public for testing
resource "aws_db_subnet_group" "public" {
  name       = "${local.name_prefix}-public-db-subnet-group"
  subnet_ids = aws_subnet.public[*].id
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-subnet-group"
  })
}
