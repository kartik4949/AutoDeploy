#!/bin/bash

while ! nc -z rabbitmq 5672; do sleep 3; done
env CONFIG=/app/configs/iris/config.yaml python3 /app/autodeploy/deploy.py
