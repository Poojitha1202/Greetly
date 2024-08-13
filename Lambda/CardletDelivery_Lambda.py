import boto3
import json
import logging

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB table name - replace with your actual table name
CARDLET_METADATA_TABLE = 'GreetlyCardletMetadataTable'

# Initialize AWS SDK clients
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

def get_cardlet_metadata(cardlet_id):
    table = dynamodb.Table(CARDLET_METADATA_TABLE)
    try:
        item = table.get_item(Key={'cardletId': cardlet_id})
        return item.get('Item')
    except Exception as e:
        logger.error(f"Error retrieving cardlet metadata: {e}")
        return None

def send_notification(topic_arn, message):
    try:
        return sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject='Your Greetly Cardlet is Ready!'
        )
    except Exception as e:
        logger.error(f"Error sending SNS notification: {e}")
        return None

def lambda_handler(event, context):
    cardlet_id = event['cardletId']
    metadata = get_cardlet_metadata(cardlet_id)
    
    if not metadata:
        logger.info(f"No data found for cardletId: {cardlet_id}")
        return {'statusCode': 404, 'body': 'Metadata not found'}

    parts = [
        f"Hello {metadata['toName']},",
        f"You have received a Greetly Cardlet from {metadata['fromName']}!",
        "Here's the message:",
        metadata.get('textContent', ''),
        "Extracted text from the cardlet image:",
        metadata.get('extractedText', ''),
        "Enjoy your day!"
    ]

    full_message = "\n\n".join(parts)

    sns_response = send_notification(metadata['snsTopicArn'], full_message)
    if not sns_response:
        return {'statusCode': 500, 'body': 'Failed to send notification'}

    return {'statusCode': 200, 'body': 'Cardlet delivered successfully'}
