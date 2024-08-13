import boto3
import json
import logging
from datetime import datetime, timedelta

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS SDK clients
eventbridge = boto3.client('events')
lambda_client = boto3.client('lambda')

# Define the time difference for Halifax
HALIFAX_TIME_DIFFERENCE_HOURS = -3

def lambda_handler(event, context):
    processed_records = []
    arn_parts = context.invoked_function_arn.split(":")
    region = arn_parts[3]
    account_id = arn_parts[4]
    
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            process_record(record, region, account_id, processed_records)
    
    return {'processedRecords': processed_records}

def process_record(record, region, account_id, processed_records):
    new_image = record['dynamodb']['NewImage']
    
    cardlet_id = new_image['cardletId']['S']
    delivery_date = new_image['deliveryDate']['S']
    email = new_image['email']['S']

    cron_expression = convert_date_to_cron(delivery_date)
    rule_name = f'CardletDelivery-{cardlet_id}'
    rule_arn = f'arn:aws:events:{region}:{account_id}:rule/{rule_name}'

    try:
        setup_eventbridge_rule(rule_name, cron_expression, cardlet_id, email)
        setup_target_and_permissions(cardlet_id, rule_name, rule_arn, email, processed_records)
    except Exception as e:
        logger.error(f"Error in processing record for cardlet {cardlet_id}: {e}")
        processed_records.append({
            'cardletId': cardlet_id,
            'ruleName': rule_name,
            'status': 'Error',
            'error': str(e)
        })

def setup_eventbridge_rule(rule_name, cron_expression, cardlet_id, email):
    eventbridge.put_rule(
        Name=rule_name,
        ScheduleExpression=cron_expression,
        State='ENABLED',
        Description=f'Schedule delivery of cardlet {cardlet_id} to {email}'
    )

def setup_target_and_permissions(cardlet_id, rule_name, rule_arn, email, processed_records):
    target_arn = 'arn:aws:lambda:us-east-1:498038081978:function:CardletDeliveryLambda'

    eventbridge.put_targets(
        Rule=rule_name,
        Targets=[{
            'Id': f'TargetFor-{cardlet_id}',
            'Arn': target_arn,
            'Input': json.dumps({'cardletId': cardlet_id, 'email': email})
        }]
    )
    
    add_invoke_permission(target_arn, rule_arn)
    processed_records.append({
        'cardletId': cardlet_id,
        'ruleName': rule_name,
        'status': 'Success'
    })
    logger.info(f"Rule created: {rule_name} for cardlet {cardlet_id}")

def add_invoke_permission(lambda_arn, rule_arn):
    rule_name_part = rule_arn.split('/')[-1]
    statement_id = f"EventBridgeInvoke-{rule_name_part}".replace('/', '-').replace(':', '-')
    try:
        lambda_client.add_permission(
            FunctionName=lambda_arn,
            StatementId=statement_id,
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=rule_arn
        )
        logger.info(f"Permission added for {lambda_arn} with {rule_arn}")
    except lambda_client.exceptions.ResourceConflictException:
        logger.info(f"Permission already exists for {lambda_arn} with {rule_arn}")
    except Exception as e:
        logger.error(f"Error in adding permission for {lambda_arn}: {e}")

def convert_date_to_cron(delivery_date):
    date_time_obj = datetime.fromisoformat(delivery_date)
    adjusted_date_time_obj = date_time_obj + timedelta(hours=HALIFAX_TIME_DIFFERENCE_HOURS)
    year, month, day, hour, minute = adjusted_date_time_obj.year, adjusted_date_time_obj.month, adjusted_date_time_obj.day, adjusted_date_time_obj.hour, adjusted_date_time_obj.minute
    cron_expression = f'cron({minute} {hour} {day} {month} ? {year})'
    return cron_expression
