from flask import Flask, request, jsonify, Blueprint
import boto3 

app = Flask(__name__)

registration_blueprint = Blueprint('registration_blueprint', __name__)

@registration_blueprint.after_request
def add_headers(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With")
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "POST")
    return response

aws_region = 'us-east-1'

# AWS configuration
dynamodb = boto3.resource('dynamodb', region_name=aws_region)
table_name = 'GreetlyUserRegistrationTable'

sns = boto3.client('sns', region_name=aws_region)

@registration_blueprint.route('/register', methods=['POST'])
def register():
    try:
        registration_data = request.get_json()
        full_name = registration_data.get('FullName')
        email = registration_data.get('Email')
        password = registration_data.get('Password')
        confirm_password = registration_data.get('confirmPassword')

        if not all([full_name, email, password, confirm_password]):
            return jsonify({'message': 'All fields are required.'}), 400

        if password != confirm_password:
            return jsonify({'message': 'Passwords do not match.'}), 400

        table = dynamodb.Table(table_name)
        existing_user = table.get_item(Key={'Email': email})

        if 'Item' in existing_user:
            return jsonify({'message': 'Email already exists.'}), 409

        # Add the new user to the DynamoDB table
        table.put_item(Item={'FullName': full_name, 'Email': email, 'Password': password})
        return jsonify({'message': 'Registration successful.'}), 201

    except Exception as e:
        return jsonify({'message': 'Error during registration.', 'error': str(e)}), 500

# Register the blueprint
app.register_blueprint(registration_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
