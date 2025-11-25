# Stack 1: VPC, Aurora Serverless, and S3
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
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

# VPC Module
module "vpc" {
  source = "../modules/vpc"
  
  name_prefix = local.name_prefix
  vpc_cidr    = var.vpc_cidr
  common_tags = local.common_tags
}

# Aurora Serverless Module
module "aurora_serverless" {
  source = "../modules/aurora_serverless"
  
  name_prefix           = local.name_prefix
  database_name         = var.database_name
  db_master_username    = var.db_master_username
  vpc_id               = module.vpc.vpc_id
  private_subnet_ids   = module.vpc.private_subnet_ids
  common_tags          = local.common_tags
}

# S3 Module
module "s3" {
  source = "../modules/s3"
  
  name_prefix = local.name_prefix
  common_tags = local.common_tags
}