# Bedrock Knowledge Base Module
data "aws_caller_identity" "current" {}

# Bedrock User Secret for Aurora access
resource "random_password" "bedrock_user_password" {
  length  = 16
  special = true
}

resource "aws_secretsmanager_secret" "bedrock_user" {
  name                    = "${var.name_prefix}-bedrock-user"
  description             = "Secret for Bedrock Knowledge Base to interact with Aurora Cluster"
  recovery_window_in_days = 7
  
  tags = var.common_tags
}

resource "aws_secretsmanager_secret_version" "bedrock_user" {
  secret_id = aws_secretsmanager_secret.bedrock_user.id
  secret_string = jsonencode({
    username = "bedrock_user"
    password = random_password.bedrock_user_password.result
  })
}

# IAM Role for Bedrock Knowledge Base
resource "aws_iam_role" "bedrock_kb" {
  name = "${var.name_prefix}-bedrock-kb-role"
  
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
            "aws:SourceArn" = "arn:aws:bedrock:${data.aws_caller_identity.current.region}:${data.aws_caller_identity.current.account_id}:knowledge-base/*"
          }
        }
      }
    ]
  })
  
  tags = var.common_tags
}

# IAM Policy for Bedrock Knowledge Base
resource "aws_iam_role_policy" "bedrock_kb" {
  name = "${var.name_prefix}-bedrock-kb-policy"
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
          var.documents_bucket_arn,
          "${var.documents_bucket_arn}/*"
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
          "rds:DescribeDBClusters",
          "rds:DescribeDBInstances"
        ]
        Resource = var.aurora_cluster_arn
      },
      {
        Effect = "Allow"
        Action = [
          "rds-data:ExecuteStatement",
          "rds-data:BatchExecuteStatement",
          "rds-data:BeginTransaction",
          "rds-data:CommitTransaction",
          "rds-data:RollbackTransaction"
        ]
        Resource = var.aurora_cluster_arn
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          var.rds_secret_arn,
          aws_secretsmanager_secret.bedrock_user.arn
        ]
      }
    ]
  })
}

# Bedrock Knowledge Base
resource "aws_bedrockagent_knowledge_base" "doc_query_kb" {
  name     = "doc-query-kb"
  role_arn = aws_iam_role.bedrock_kb.arn
  
  knowledge_base_configuration {
    vector_knowledge_base_configuration {
      embedding_model_arn = var.kb_embedding_model_arn
    }
    type = "VECTOR"
  }
  
  storage_configuration {
    type = "RDS"
    rds_configuration {
      credentials_secret_arn = aws_secretsmanager_secret.bedrock_user.arn
      database_name         = var.database_name
      field_mapping {
        metadata_field    = "metadata"
        primary_key_field = "id"
        text_field       = "chunks"
        vector_field     = "embedding"
      }
      resource_arn = var.aurora_cluster_arn
      table_name   = "bedrock_integration.bedrock_knowledge_base"
    }
  }
  
  tags = var.common_tags
}

# Data Source for Knowledge Base
resource "aws_bedrockagent_data_source" "s3_documents" {
  knowledge_base_id = aws_bedrockagent_knowledge_base.doc_query_kb.id
  name             = "s3-documents"
  
  data_source_configuration {
    type = "S3"
    s3_configuration {
      bucket_arn = var.documents_bucket_arn
    }
  }
}