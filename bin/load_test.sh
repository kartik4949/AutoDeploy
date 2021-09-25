#!/bin/bash

# load testing bash script
helpFunction()
{
   echo ""
   echo "Usage: $0 -f /app/configs/config.yaml"
   echo -e "\t-f A configuration file for deployment."
   exit 1 
}

while getopts "f:" opt
do
   case "$opt" in
      f ) parameterF="$OPTARG" ;;
      ? ) helpFunction ;; 
   esac
done

if [ -z "$parameterF" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct
echo "$parameterF"
cd ./autodeploy/
env CONFIG=$parameterF locust -f testing/load_test.py
