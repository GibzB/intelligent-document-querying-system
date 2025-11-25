variable "name_prefix" {
  description = "Name prefix for resources"
  type        = string
}

variable "aurora_cluster_arn" {
  description = "ARN of the Aurora cluster"
  type        = string
}

variable "documents_bucket_arn" {
  description = "ARN of the S3 documents bucket"
  type        = string
}

variable "rds_secret_arn" {
  description = "ARN of the RDS credentials secret"
  type        = string
}

variable "database_name" {
  description = "Name of the Aurora database"
  type        = string
}

variable "kb_embedding_model_arn" {
  description = "ARN of the embedding model for Knowledge Base"
  type        = string
}

variable "kb_foundation_model_arn" {
  description = "ARN of the foundation model for Knowledge Base"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}