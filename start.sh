#!/bin/bash

# python3 /app/autodeploy/monitor.py
while ! nc -z rabbitmq 5672; do sleep 3; done
env CONFIG='/app/configs/object_detection/config.yaml' python3 /app/autodeploy/deploy.py