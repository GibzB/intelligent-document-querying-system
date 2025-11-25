variable "name_prefix" {
  description = "Name prefix for resources"
  type        = string
}

variable "database_name" {
  description = "Name of the Aurora database"
  type        = string
}

variable "db_master_username" {
  description = "Master username for Aurora database"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where Aurora will be deployed"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for Aurora"
  type        = list(string)
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}