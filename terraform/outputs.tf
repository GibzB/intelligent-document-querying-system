# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

# RDS Outputs
output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres_budget.endpoint
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.postgres_budget.db_name
}

# Secrets Manager Output
output "rds_secret_arn" {
  description = "ARN of RDS credentials secret"
  value       = aws_secretsmanager_secret.rds_credentials.arn
}

output "rds_secret_name" {
  description = "Name of RDS credentials secret"
  value       = aws_secretsmanager_secret.rds_credentials.name
}

# S3 Outputs
output "documents_bucket_name" {
  description = "Name of the S3 bucket for documents"
  value       = aws_s3_bucket.documents.id
}

# Knowledge Base Outputs
output "bedrock_kb_role_arn" {
  description = "ARN of the IAM role for Bedrock Knowledge Base"
  value       = aws_iam_role.bedrock_kb.arn
}

output "knowledge_base_id" {
  description = "ID of the Bedrock Knowledge Base"
  value       = aws_bedrockagent_knowledge_base.doc_query_kb.id
}

output "knowledge_base_arn" {
  description = "ARN of the Bedrock Knowledge Base"
  value       = aws_bedrockagent_knowledge_base.doc_query_kb.arn
}

output "aurora_cluster_arn" {
  description = "ARN of the Aurora cluster"
  value       = aws_rds_cluster.aurora_cluster.arn
}

# Next Steps
output "next_steps" {
  description = "Next steps for setup"
  value       = <<-EOT
    Next Steps:
    1. Get database password: aws secretsmanager get-secret-value --secret-id ${aws_secretsmanager_secret.rds_credentials.name}
    2. Connect to database and install pgvector extension
    3. Upload documents to S3: aws s3 cp your-document.pdf s3://${aws_s3_bucket.documents.id}/
    4. Create Bedrock Knowledge Base in AWS Console
  EOT
}
