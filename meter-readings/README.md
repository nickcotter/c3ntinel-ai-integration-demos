This is a demo of using OpenAI vision to submit meter readings to the C3NTINEL meter readings API.


# C3NTINEL API

TODO

# OPENAI VISION API

TODO

# Deployment

~~~~
aws cloudformation deploy \
  --template-file meter-photo-processor.yaml \
  --stack-name meter-demo \
  --parameter-overrides LambdaS3Key=lambda/meter-reader.zip LambdaS3Bucket=your-bucket-name \
  --capabilities CAPABILITY_NAMED_IAM
~~~~
