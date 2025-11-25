# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = module.vpc.private_subnet_ids
}

# Aurora Outputs
output "aurora_cluster_arn" {
  description = "Aurora cluster ARN"
  value       = module.aurora_serverless.cluster_arn
}

output "aurora_cluster_endpoint" {
  description = "Aurora cluster endpoint"
  value       = module.aurora_serverless.cluster_endpoint
}

output "database_name" {
  description = "Database name"
  value       = module.aurora_serverless.database_name
}

output "rds_secret_arn" {
  description = "ARN of RDS credentials secret"
  value       = module.aurora_serverless.secret_arn
}

output "rds_secret_name" {
  description = "Name of RDS credentials secret"
  value       = module.aurora_serverless.secret_name
}

# S3 Outputs
output "documents_bucket_name" {
  description = "Name of the S3 bucket for documents"
  value       = module.s3.bucket_name
}

output "documents_bucket_arn" {
  description = "ARN of the S3 bucket for documents"
  value       = module.s3.bucket_arn
}