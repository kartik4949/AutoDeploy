#!/bin/bash

while ! nc -z rabbitmq 5672; do sleep 3; done
python3 /app/autodeploy/api.py
