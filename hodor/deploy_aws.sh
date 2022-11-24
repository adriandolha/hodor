#!/bin/bash

APP_REGION="eu-central-1"
# aws ecr create-repository --repository-name hodor --region $APP_REGION
ECR=${1-"103050589342.dkr.ecr.eu-central-1.amazonaws.com/hodor"}
# aws ecr get-login-password --region $APP_REGION | docker login --username AWS --password-stdin $ECR
VERSION=${2-"v8"}
docker build -t hodor:$VERSION .
docker tag hodor:$VERSION $ECR:$VERSION
docker push $ECR:$VERSION
