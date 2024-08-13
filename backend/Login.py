from flask import Flask, request, jsonify, Blueprint
import boto3

# Define a Flask Blueprint for handling login routes
auth_blueprint = Blueprint('auth_blueprint', __name__)

app = Flask(__name__)

# Middleware to enable CORS and set response headers
@auth_blueprint.after_request
def setup_cors(response):
    response.headers['Access-Control-Allow-Headers'] = "Content-Type, Authorization, X-Requested-With"
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    return response

# Configuration for AWS and DynamoDB
region = 'us-east-1'
dynamodb = boto3.resource('dynamodb', region_name=region)
users_table = 'GreetlyUserRegistrationTable'
notification_service = boto3.client('sns', region_name=region)

@auth_blueprint.route('/login', methods=['POST'])
def handle_login():
    login_details = request.get_json()
    user_email = login_details.get('Email')
    user_password = login_details.get('Password')

    if not user_email or not user_password:
        return jsonify({'message': 'Missing email or password'}), 400

    user_table = dynamodb.Table(users_table)
    user_response = user_table.get_item(Key={'Email': user_email})

    if 'Item' not in user_response:
        return jsonify({'message': 'User not found'}), 404

    stored_password = user_response['Item']['Password']
    if stored_password != user_password:
        return jsonify({'message': 'Password mismatch'}), 401

    return process_successful_login(user_email)

def process_successful_login(email):
    topic_id = f"UserNotification-{email.split('@')[0]}"
    existing_topics = notification_service.list_topics()

    if not any(topic_id in topic['TopicArn'] for topic in existing_topics['Topics']):
        new_topic = notification_service.create_topic(Name=topic_id)
        topic_arn = new_topic['TopicArn']
        notification_service.subscribe(TopicArn=topic_arn, Protocol='email', Endpoint=email)
        return jsonify({'message': 'Logged in successfully', 'topic_arn': topic_arn}), 200

    return jsonify({'message': 'Logged in successfully'}), 200

# References and documentation links provided in comments for clarity and further reading.
