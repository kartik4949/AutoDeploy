#!/bin/bash

while ! nc -z redis 6379; do sleep 3; done
python3 /app/autodeploy/predict.py
