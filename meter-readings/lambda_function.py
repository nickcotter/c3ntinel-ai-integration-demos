import boto3
import os
import base64
import openai
import requests
from datetime import datetime

openai.api_key = os.environ['OPENAI_API_KEY']

def get_oauth_token():
    """Request OAuth token using client credentials."""
    response = requests.post(os.environ['OAUTH_TOKEN_URL'], data={
        'grant_type': 'client_credentials',
        'client_id': os.environ['OAUTH_CLIENT_ID'],
        'client_secret': os.environ['OAUTH_CLIENT_SECRET']
    })
    response.raise_for_status()
    return response.json()['access_token']

def extract_meter_reading(image_bytes: bytes) -> float:
    """Send image to OpenAI Vision API and return the numeric reading."""
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    result = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "What is the numeric meter reading shown in this image? Respond with only the number."},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
            ]}
        ]
    )
    return float(result.choices[0].message.content.strip())

def submit_reading_to_api(reading: float, source_key: str, token: str):
    """Submit reading to the REST API using OAuth token."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Sample meterId (replace with dynamic value if needed)
    meter_id = 161812

    # Current timestamp in both formats
    now = datetime.utcnow()
    payload = {
        "manualReading": {
            "enteredDate": now.strftime("%d/%m/%Y %H:%M:%S"),
            "status": "OK",
            "time": int(now.timestamp() * 1000),
            "value": reading
        },
        "meterId": meter_id
    }

    response = requests.post(os.environ['METER_API_URL'], json=payload, headers=headers)
    response.raise_for_status()

def lambda_handler(event, context):
    """AWS Lambda entry point."""
    try:
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        print(f"Processing image from: s3://{bucket}/{key}")

        # Download image from S3
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=bucket, Key=key)
        image_bytes = obj['Body'].read()

        # Extract meter reading
        reading = extract_meter_reading(image_bytes)
        print(f"Extracted meter reading: {reading}")

        # Get OAuth token
        token = get_oauth_token()

        # Submit to API
        submit_reading_to_api(reading, source_key=key, token=token)

        return {
            'statusCode': 200,
            'body': f"Reading {reading} submitted successfully."
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': f"Error processing image: {str(e)}"
        }
