This is a demo of using OpenAI vision to submit meter readings to the C3NTINEL meter readings API.

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

Create a bucket for deployments - use it to upload the funciton zip.

> aws s3 cp function.zip s3://lambda-bucket-name/lambda/meter-photo-processor-function.zip


## Create the photos bucket

This can be anything you want. You will need to upload photos here.

## Creating The Stack

~~~~
aws cloudformation deploy \
  --template-file meter-photo-processor.yaml \
  --stack-name meter-photo-processor-demo \
  --parameter-overrides \
      LambdaS3Key=lambda/meter-photo-processor-function.zip \
      LambdaS3Bucket=lambda-bucket-name \
      PhotoBucketName=your-photo-bucket \
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
