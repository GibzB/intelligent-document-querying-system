variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "doc-query-system"
}

variable "database_name" {
  description = "Name of the Aurora database"
  type        = string
  default     = "vectordb"
}

# Inputs from Stack 1
variable "aurora_cluster_arn" {
  description = "ARN of the Aurora cluster from Stack 1"
  type        = string
}

variable "documents_bucket_arn" {
  description = "ARN of the S3 documents bucket from Stack 1"
  type        = string
}

variable "rds_secret_arn" {
  description = "ARN of the RDS credentials secret from Stack 1"
  type        = string
}

variable "kb_embedding_model_arn" {
  description = "ARN of the embedding model for Knowledge Base"
  type        = string
  default     = "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
}

variable "kb_foundation_model_arn" {
  description = "ARN of the foundation model for Knowledge Base"
  type        = string
  default     = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
}