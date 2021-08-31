#!/bin/bash

# python3 /app/autodeploy/monitor.py
while ! nc -z rabbitmq 5672; do sleep 3; done
python3 /app/autodeploy/deploy.py