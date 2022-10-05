#!/bin/bash
docker build -t hodor:dev .
kubectl delete -f app.yaml --ignore-not-found
kubectl apply -f app.yaml