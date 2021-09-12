#!/bin/bash

# docker compose commands to start the autodeploy service.
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
CONFIG=$parameterF docker-compose build
CONFIG=$parameterF docker-compose up
