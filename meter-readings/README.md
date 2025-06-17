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

## Uploading Lambda Zip

> aws s3 cp function.zip s3://your-deployment-bucket/lambda/function.zip

## Creating The Stack

~~~~
aws cloudformation deploy \
  --template-file meter-photo-processor.yaml \
  --stack-name meter-demo \
  --parameter-overrides \
      LambdaS3Key=lambda/function.zip \
      LambdaS3Bucket=your-deployment-bucket \
  --capabilities CAPABILITY_NAMED_IAM
~~~~
