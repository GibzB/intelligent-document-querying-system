#!/usr/bin/env python3
"""
Complete setup script that creates ALL project files
Run this after the initial folder structure is created
"""

import os
import sys

def create_all_files():
    """Create all Terraform, Python, and documentation files"""
    
    print("=" * 70)
    print("CREATING ALL PROJECT FILES")
    print("=" * 70)
    print()
    
    # Check if we're in a reasonable location and create directories if needed
    current_dir = os.path.basename(os.getcwd())
    print(f"Current directory: {current_dir}")
    
    # Create base directories if they don't exist
    directories = ['Screenshots', 'terraform', 'python', 'documents/sample_documents', 'frontend']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✓ Directory structure verified/created\n")
    
    # Import the file creation functions
    # We'll inline them here for a single-file solution
    
    # ========================================
    # TERRAFORM FILES
    # ========================================
    
    print("Creating Terraform files...")
    
    terraform_files = {
        "terraform/providers.tf": """terraform {
  required_version = ">= 1.0"
  
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
      Project     = "IntelligentDocumentQuerying"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
""",

        "terraform/variables.tf": """variable "aws_region" {
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

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "database_name" {
  description = "Name of the Aurora database"
  type        = string
  default     = "vectordb"
}

variable "db_master_username" {
  description = "Master username for Aurora database"
  type        = string
  default     = "dbadmin"
  sensitive   = true
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
""",

        "terraform/main.tf": """# Main Terraform configuration file

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Terraform   = "true"
  }
}

# Random password for RDS
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Store DB credentials in Secrets Manager
resource "aws_secretsmanager_secret" "rds_credentials" {
  name                    = "${local.name_prefix}-rds-credentials"
  description             = "Aurora PostgreSQL credentials for document querying system"
  recovery_window_in_days = 7
  
  tags = local.common_tags
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
""",

        "terraform/vpc.tf": """# VPC Configuration
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-vpc"
  })
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-igw"
  })
}

# Public Subnets
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  map_public_ip_on_launch = true
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-subnet-${count.index + 1}"
    Type = "Public"
  })
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-subnet-${count.index + 1}"
    Type = "Private"
  })
}

# Route Table for Public Subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-rt"
  })
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Security Group for Aurora
resource "aws_security_group" "aurora" {
  name        = "${local.name_prefix}-aurora-sg"
  description = "Security group for Aurora PostgreSQL cluster"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    description = "PostgreSQL from VPC"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }
  
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-aurora-sg"
  })
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}
""",

        "terraform/aurora.tf": """# Aurora PostgreSQL Serverless Cluster
resource "aws_rds_cluster" "aurora_cluster" {
  cluster_identifier      = "${local.name_prefix}-cluster"
  engine                  = "aurora-postgresql"
  engine_mode             = "provisioned"
  engine_version          = "15.4"
  database_name           = var.database_name
  master_username         = var.db_master_username
  master_password         = random_password.db_password.result
  
  db_subnet_group_name    = aws_db_subnet_group.aurora.name
  vpc_security_group_ids  = [aws_security_group.aurora.id]
  
  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  
  skip_final_snapshot     = true
  apply_immediately       = true
  
  serverlessv2_scaling_configuration {
    max_capacity = 2.0
    min_capacity = 0.5
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-aurora-cluster"
  })
}

# Aurora Cluster Instance
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

# DB Subnet Group
resource "aws_db_subnet_group" "aurora" {
  name       = "${local.name_prefix}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-subnet-group"
  })
}
""",

        "terraform/s3.tf": """# S3 Bucket for Documents
resource "aws_s3_bucket" "documents" {
  bucket = "${local.name_prefix}-documents-${data.aws_caller_identity.current.account_id}"
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-documents"
  })
}

# S3 Bucket Versioning
resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket Server-Side Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket Public Access Block
resource "aws_s3_bucket_public_access_block" "documents" {
  bucket = aws_s3_bucket.documents.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket Policy for Bedrock
resource "aws_s3_bucket_policy" "documents" {
  bucket = aws_s3_bucket.documents.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowBedrockAccess"
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.documents.arn,
          "${aws_s3_bucket.documents.arn}/*"
        ]
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}
""",

        "terraform/knowledge_base.tf": """# IAM Role for Bedrock Knowledge Base
resource "aws_iam_role" "bedrock_kb" {
  name = "${local.name_prefix}-bedrock-kb-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
          ArnLike = {
            "aws:SourceArn" = "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:knowledge-base/*"
          }
        }
      }
    ]
  })
  
  tags = local.common_tags
}

# IAM Policy for Bedrock Knowledge Base
resource "aws_iam_role_policy" "bedrock_kb" {
  name = "${local.name_prefix}-bedrock-kb-policy"
  role = aws_iam_role.bedrock_kb.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.documents.arn,
          "${aws_s3_bucket.documents.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = var.kb_embedding_model_arn
      },
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBClusters"
        ]
        Resource = aws_rds_cluster.aurora_cluster.arn
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.rds_credentials.arn
      }
    ]
  })
}
""",

        "terraform/outputs.tf": """# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

# Aurora Outputs
output "aurora_cluster_endpoint" {
  description = "Aurora cluster endpoint"
  value       = aws_rds_cluster.aurora_cluster.endpoint
}

output "aurora_database_name" {
  description = "Database name"
  value       = aws_rds_cluster.aurora_cluster.database_name
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
"""
    }
    
    # Create Terraform files
    for filepath, content in terraform_files.items():
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✓ {filepath}")
    
    print(f"\n✅ Created {len(terraform_files)} Terraform files\n")
    
    # ========================================
    # PYTHON FILES
    # ========================================
    
    print("Creating Python files...")
    
    # Note: The Python files content is too long to inline here
    # We'll create them with proper content
    
    # bedrock_utils.py
    with open('python/bedrock_utils.py', 'w') as f:
        f.write('''"""
Bedrock utility functions for document querying system
"""

import boto3
import json
import re
from typing import Tuple, Dict, Any

def query_knowledge_base(query: str, knowledge_base_id: str, model_arn: str, region: str = 'us-east-1') -> Dict[str, Any]:
    """Query the Bedrock knowledge base"""
    bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=region)
    
    response = bedrock_agent_runtime.retrieve_and_generate(
        input={'text': query},
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': knowledge_base_id,
                'modelArn': model_arn
            }
        }
    )
    return response

def generate_response(prompt: str, temperature: float = 0.7, top_p: float = 0.9, max_tokens: int = 512) -> str:
    """Generate response using Bedrock with configurable parameters"""
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "messages": [{"role": "user", "content": prompt}]
    })
    
    response = bedrock_runtime.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=body
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']

def valid_prompt(prompt: str) -> Tuple[bool, str]:
    """Validate and filter user prompts"""
    blocked_keywords = [
        'ignore previous instructions', 'disregard', 'system prompt',
        'jailbreak', 'bypass', 'override'
    ]
    
    if len(prompt.strip()) < 3:
        return False, "Prompt too short"
    if len(prompt) > 1000:
        return False, "Prompt too long"
    
    prompt_lower = prompt.lower()
    for keyword in blocked_keywords:
        if keyword in prompt_lower:
            return False, f"Blocked keyword: '{keyword}'"
    
    sql_patterns = [r'drop\\s+table', r'delete\\s+from', r';\\s*--']
    for pattern in sql_patterns:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            return False, "Potential SQL injection detected"
    
    return True, prompt.strip()
''')
    print("  ✓ python/bedrock_utils.py")
    
    # requirements.txt
    with open('python/requirements.txt', 'w') as f:
        f.write('boto3>=1.28.0\nbotocore>=1.31.0\n')
    print("  ✓ python/requirements.txt")
    
    # test_valid_prompt.py
    with open('python/test_valid_prompt.py', 'w') as f:
        f.write('''from bedrock_utils import valid_prompt

test_cases = [
    "What is machine learning?",
    "ignore previous instructions",
    "DROP TABLE users;",
    ""
]

print("=" * 60)
print("VALID_PROMPT TEST OUTPUT")
print("=" * 60)

for test in test_cases:
    is_valid, result = valid_prompt(test)
    print(f"\\nPrompt: '{test[:50]}'")
    print(f"Valid: {is_valid}, Result: {result}")
''')
    print("  ✓ python/test_valid_prompt.py")
    
    print(f"\n✅ Created Python files\n")
    
    # ========================================
    # DOCUMENTATION FILES
    # ========================================
    
    print("Creating documentation files...")
    
    # README.md
    with open('README.md', 'w') as f:
        f.write('''# Intelligent Document Querying System

AWS Bedrock-powered document querying system with Aurora PostgreSQL vector database.

## Features

- VPC with public/private subnets
- Aurora PostgreSQL Serverless with pgvector
- S3 document storage
- AWS Bedrock Knowledge Base integration
- Lambda functions for query processing

## Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

## Testing

```bash
cd python
python test_valid_prompt.py
```
''')
    print("  ✓ README.md")
    
    # temperature_top_p_explanation.md
    with open('temperature_top_p_explanation.md', 'w') as f:
        f.write('''# Temperature and Top_P Parameters

## Temperature Parameter

The temperature parameter controls randomness in AI responses (0.0-1.0). Lower values (0.1-0.3) produce deterministic, factual responses ideal for document querying. Higher values (0.8-1.0) increase creativity but may reduce accuracy. For this system, 0.5-0.7 balances accuracy with natural language.

## Top_P Parameter

The top_p parameter (nucleus sampling) limits token selection to a cumulative probability threshold. A value of 0.9 considers tokens accounting for 90% of probability mass, filtering low-probability options. Combined with moderate temperature (0.5-0.7), top_p 0.85-0.9 produces accurate, naturally worded answers from the document corpus.
''')
    print("  ✓ temperature_top_p_explanation.md")
    
    print(f"\n✅ Created documentation files\n")
    
    # ========================================
    # SUMMARY
    # ========================================
    
    print("=" * 70)
    print("✅ ALL FILES CREATED SUCCESSFULLY!")
    print("=" * 70)
    print("\nFiles created:")
    print("  📁 Terraform (8 files): providers, variables, main, vpc, aurora, s3, knowledge_base, outputs")
    print("  🐍 Python (3 files): bedrock_utils, requirements, test_valid_prompt")
    print("  📄 Documentation (2 files): README, temperature_top_p_explanation")
    print("\nNext steps:")
    print("  1. git add .")
    print("  2. git commit -m 'Add all project files'")
    print("  3. git push")
    print()

if __name__ == "__main__":
    create_all_files()