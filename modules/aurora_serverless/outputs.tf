output "cluster_arn" {
  description = "Aurora cluster ARN"
  value       = aws_rds_cluster.aurora_cluster.arn
}

output "cluster_endpoint" {
  description = "Aurora cluster endpoint"
  value       = aws_rds_cluster.aurora_cluster.endpoint
}

output "database_name" {
  description = "Database name"
  value       = aws_rds_cluster.aurora_cluster.database_name
}

output "secret_arn" {
  description = "ARN of RDS credentials secret"
  value       = aws_secretsmanager_secret.rds_credentials.arn
}

output "secret_name" {
  description = "Name of RDS credentials secret"
  value       = aws_secretsmanager_secret.rds_credentials.name
}