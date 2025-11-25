# Bedrock User Secret for Aurora access
resource "aws_secretsmanager_secret" "bedrock_user" {
  name                    = "${local.name_prefix}-bedrock-user"
  description             = "Secret for Bedrock Knowledge Base to interact with Aurora Cluster"
  recovery_window_in_days = 7
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "bedrock_user" {
  secret_id = aws_secretsmanager_secret.bedrock_user.id
  secret_string = jsonencode({
    username = "bedrock_user"
    password = random_password.bedrock_user_password.result
  })
}

resource "random_password" "bedrock_user_password" {
  length  = 16
  special = true
}

# Null resource to handle database setup
resource "null_resource" "aurora_setup" {
  depends_on = [aws_rds_cluster_instance.aurora_instance]
  
  provisioner "local-exec" {
    command = "echo 'Aurora cluster ready for Bedrock'"
  }
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
      resource_arn = aws_rds_cluster.aurora_cluster.arn
      table_name   = "bedrock_integration.bedrock_knowledge_base"
    }
  }
  
  tags = local.common_tags
  
  depends_on = [null_resource.aurora_setup]
}

# Data Source for Knowledge Base
resource "aws_bedrockagent_data_source" "s3_documents" {
  knowledge_base_id = aws_bedrockagent_knowledge_base.doc_query_kb.id
  name             = "s3-documents"
  
  data_source_configuration {
    type = "S3"
    s3_configuration {
      bucket_arn = aws_s3_bucket.documents.arn
    }
  }
}