This is a demo of using OpenAI vision to submit meter readings to the C3NTINEL meter readings API.


# C3NTINEL API

TODO

# OPENAI VISION API

TODO

# Deployment

## Creating Lambda Zip

~~~~
mkdir package
pip install -r requirements.txt -t package/
cp lambda_function.py package/
cd package
zip -r ../function.zip .
cd ..
~~~~

TODO github actions

## Uploading Lambda Zip

Create a bucket for deployments - eg c3ntinel-ai-experimental-lambdas

> aws s3 cp function.zip s3://c3ntinel-ai-experimental-lambdas/lambda/meter-photo-processor-function.zip


## Create the photos bucket

This can be anything you want, eg c3ntinel-ai-meter-photos

You will need to upload photos here.

## Creating The Stack

~~~~
aws cloudformation deploy \
  --template-file meter-photo-processor.yaml \
  --stack-name meter-photo-processor-demo \
  --parameter-overrides \
      LambdaS3Key=lambda/meter-photo-processor-function.zip \
      LambdaS3Bucket=c3ntinel-ai-experimental-lambdas \
      PhotoBucketName=c3ntinel-ai-meter-photos \
  --capabilities CAPABILITY_NAMED_IAM
~~~~

## Attaching Notifications

~~~~
aws s3api put-bucket-notification-configuration \
  --bucket your-photo-bucket \
  --notification-configuration '{
    "LambdaFunctionConfigurations": [
      {
        "LambdaFunctionArn": "arn:aws:lambda:REGION:ACCOUNT_ID:function:LAMBDA_NAME",
        "Events": ["s3:ObjectCreated:*"]
      }
    ]
  }'
~~~~
