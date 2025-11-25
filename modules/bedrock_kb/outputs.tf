output "knowledge_base_id" {
  description = "ID of the Bedrock Knowledge Base"
  value       = aws_bedrockagent_knowledge_base.doc_query_kb.id
}

output "knowledge_base_arn" {
  description = "ARN of the Bedrock Knowledge Base"
  value       = aws_bedrockagent_knowledge_base.doc_query_kb.arn
}

output "role_arn" {
  description = "ARN of the IAM role for Bedrock Knowledge Base"
  value       = aws_iam_role.bedrock_kb.arn
}

output "bedrock_user_secret_arn" {
  description = "ARN of the Bedrock user secret"
  value       = aws_secretsmanager_secret.bedrock_user.arn
}