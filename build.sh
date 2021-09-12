#!/bin/bash

# docker build commands to make docker images.

helpFunction()
{
   echo ""
   echo "Usage: $0 -r /app/model_dependencies/reqs.txt"
   echo -e "\t-r Path to model dependencies reqs txt."
   exit 1 
}

while getopts "r:" opt
do
   case "$opt" in
      r ) parameterR="$OPTARG" ;;
      ? ) helpFunction ;; 
   esac
done

if [ -z "$parameterR" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct
echo "$parameterR"
docker build -t autodeploy --build-arg MODEL_REQ=$parameterR -f Dockerfile .
docker build -t monitor --build-arg MODEL_REQ=$parameterR  -f MonitorDockerfile .
