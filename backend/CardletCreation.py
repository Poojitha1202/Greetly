from flask import Blueprint, request, jsonify
import boto3
import uuid
import os

cardlet_creation_app = Blueprint('cardlet_creation_app', __name__)
aws_region = 'us-east-1'

@cardlet_creation_app.after_request
def add_headers(response):
    response.headers.add("Access-Control-Allow-Headers", "Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")  
    return response

dynamodb = boto3.resource('dynamodb', region_name=aws_region)
textract = boto3.client('textract', region_name=aws_region)
s3 = boto3.client('s3', region_name=aws_region)
sns = boto3.client('sns', region_name=aws_region)

USER_REGISTRATION_TABLE = 'GreetlyUserRegistrationTable'
CARDLET_METADATA_TABLE = 'GreetlyCardletMetadataTable'
S3_BUCKET_NAME = 'greetly-textract'

@cardlet_creation_app.route('/create_cardlet', methods=['POST'])
def create_cardlet():
    data = request.form
    from_name = data['from']
    to_name = data['to']
    email = data['email']
    wishes = data['wishes']
    delivery_date = data['deliveryDate']

    # Generate a topic prefix based on the recipient's email prefix
    topic_prefix = f"CardletDeliveryTo{email.split('@')[0]}"
    
    # Checking for existing topics to avoid unnecessary creation
    sns_response = sns.list_topics()
    topics = sns_response.get('Topics', [])
    sns_topic_arn = next((topic['TopicArn'] for topic in topics if topic_prefix in topic['TopicArn']), None)

    if not sns_topic_arn:
        try:
            # Create a new SNS topic if not found
            sns_topic = sns.create_topic(Name=topic_prefix)
            sns_topic_arn = sns_topic['TopicArn']
            # Subscribe the user to the SNS topic
            sns.subscribe(
                TopicArn=sns_topic_arn,
                Protocol='email',
                Endpoint=email
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    image_data = request.files['image']
    image_file_name = str(uuid.uuid4()) + os.path.splitext(image_data.filename)[1]
    s3.upload_fileobj(image_data, S3_BUCKET_NAME, image_file_name)
    response = textract.detect_document_text(Document={'S3Object': {'Bucket': S3_BUCKET_NAME, 'Name': image_file_name}})

    # Extract text from the image
    extracted_text = ''
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE':
            extracted_text += item['Text'] + ' '

    # Generate a unique cardlet ID
    cardlet_id = str(uuid.uuid4())
    
    # Save cardlet metadata in DynamoDB
    cardlet_table = dynamodb.Table(CARDLET_METADATA_TABLE)
    cardlet_table.put_item(Item={
        'cardletId': cardlet_id,
        'from': from_name,
        'to': to_name,
        'email': email,
        'wishes': wishes,
        'deliveryDate': delivery_date,
        'extractedText': extracted_text,
        'snsTopicArn': sns_topic_arn
    })

    return jsonify({
        'cardletId': cardlet_id,
        'from': from_name,
        'to': to_name,
        'email': email,
        'wishes': wishes,
        'extractedText': extracted_text,
        'deliveryDate': delivery_date,
        'snsTopicArn': sns_topic_arn,
        'message': 'Cardlet created successfully'
    })

