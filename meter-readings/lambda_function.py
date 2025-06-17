import boto3
import os
import base64
import openai
import requests

# OpenAI setup
openai.api_key = os.environ['OPENAI_API_KEY']

def get_oauth_token():
    """Request OAuth token from the configured token endpoint."""
    response = requests.post(os.environ['OAUTH_TOKEN_URL'], data={
        'grant_type': 'client_credentials',
        'client_id': os.environ['OAUTH_CLIENT_ID'],
        'client_secret': os.environ['OAUTH_CLIENT_SECRET']
    })
    response.raise_for_status()
    return response.json()['access_token']

def extract_meter_reading(image_bytes: bytes) -> str:
    """Send image to OpenAI Vision API and extract the meter reading."""
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    result = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "What is the numeric meter reading shown in this image? Respond with only the number."},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}]}
        ]
    )
    return result.choices[0].message.content.strip()

def submit_reading_to_api(reading: str, source: str, token: str):
    """Submit the meter reading to the REST API using OAuth token."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "reading": reading,
        "source": source  # e.g., the S3 object key as metadata
    }
    response = requests.post(os.environ['METER_API_URL'], json=payload, headers=headers)
    response.raise_for_status()

def lambda_handler(event, context):
    """Main Lambda entry point."""
    try:
        # Extract S3 info from the event
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        print(f"Processing image: s3://{bucket}/{key}")

        # Download image
        s3 = boto3.client('s3')
        image_obj = s3.get_object(Bucket=bucket, Key=key)
        image_bytes = image_obj['Body'].read()

        # Extract meter reading
        reading = extract_meter_reading(image_bytes)
        print(f"Extracted meter reading: {reading}")

        # Get OAuth token
        token = get_oauth_token()

        # Submit reading to API
        submit_reading_to_api(reading, source=key, token=token)

        return {
            'statusCode': 200,
            'body': f"Successfully submitted meter reading: {reading}"
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': f"Failed to process image: {str(e)}"
        }
