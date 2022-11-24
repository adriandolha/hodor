#!/bin/bash
APP_REGION="eu-central-1"
# aws cloudformation create-stack --stack-name hodor-vpc \
#     --template-body file://vpc.yml \
#     --capabilities CAPABILITY_IAM \
#     --region $APP_REGION \
#     --parameters ParameterKey=Az1,ParameterValue="${APP_REGION}a" \
#     ParameterKey=Az2,ParameterValue="${APP_REGION}b"

# aws cloudformation create-stack --stack-name hodor-db \
#     --template-body file://db.yml \
#     --capabilities CAPABILITY_IAM \
#     --region $APP_REGION

# aws cloudformation create-stack --stack-name hodor-ecs \
#     --template-body file://ecs.yml \
#     --capabilities CAPABILITY_IAM \
#     --region $APP_REGION

aws cloudformation update-stack --stack-name hodor-ecs \
    --template-body file://ecs.yml \
    --capabilities CAPABILITY_IAM \
    --region $APP_REGION

