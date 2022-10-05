#!/bin/bash
echo Postgres password:
read password
helm del postgres
helm install postgres bitnami/postgresql -n hodor\
    --set postgresqlPassword=$password,postgresqlDatabase=hodor