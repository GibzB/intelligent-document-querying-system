# Stack 2: Bedrock Knowledge Base
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      ManagedBy = "Terraform"
    }
  }
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Terraform   = "true"
  }
}

# Bedrock Knowledge Base Module
module "bedrock_kb" {
  source = "../modules/bedrock_kb"
  
  name_prefix                = local.name_prefix
  aurora_cluster_arn         = var.aurora_cluster_arn
  documents_bucket_arn       = var.documents_bucket_arn
  rds_secret_arn            = var.rds_secret_arn
  database_name             = var.database_name
  kb_embedding_model_arn    = var.kb_embedding_model_arn
  kb_foundation_model_arn   = var.kb_foundation_model_arn
  common_tags               = local.common_tags
}