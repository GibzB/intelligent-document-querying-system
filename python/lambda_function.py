import json
import os
from bedrock_utils import query_knowledge_base, generate_response, valid_prompt, query_with_sources

def lambda_handler(event, context):
    """
    AWS Lambda function to handle document querying requests.
    """
    try:
        # Extract query from event
        body = json.loads(event.get('body', '{}'))
        query = body.get('query', '')
        
        # Validate the prompt
        is_valid, validation_result = valid_prompt(query)
        if not is_valid:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': validation_result
                })
            }
        
        # Get environment variables
        knowledge_base_id = os.environ.get('KNOWLEDGE_BASE_ID')
        model_arn = os.environ.get('MODEL_ARN', 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0')
        
        if not knowledge_base_id:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Knowledge base ID not configured'
                })
            }
        
        # Query the knowledge base
        response = query_with_sources(validation_result, knowledge_base_id, model_arn)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'answer': response['answer'],
                'sources': response['sources'],
                'query': validation_result
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }