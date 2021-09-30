#!/bin/bash

# docker build commands to make docker images.

helpFunction()
{
   echo ""
   echo "Usage: $0 -r /app/model_dependencies/reqs.txt -c model configuration file."
   echo -e "\t-r Path to model dependencies reqs txt."
   echo -e "\t-c Path to model configuration."
   exit 1 
}

while getopts "r:c:" opt
do
   case "$opt" in
      r ) parameterR="$OPTARG" ;;
      c ) parameterC="$OPTARG" ;;
      ? ) helpFunction ;; 
   esac
done

if [ -z "$parameterR" ] || [ -z "$parameterC" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct
echo "$parameterR"
docker build -t autodeploy --build-arg MODEL_REQ=$parameterR --build-arg MODEL_CONFIG=$parameterC  -f docker/Dockerfile .
docker build -t prediction --build-arg MODEL_REQ=$parameterR --build-arg MODEL_CONFIG=$parameterC -f docker/PredictDockerfile .
docker build -t monitor --build-arg MODEL_REQ=$parameterR  --build-arg MODEL_CONFIG=$parameterC -f docker/MonitorDockerfile .
docker build -t prometheus_server  -f docker/PrometheusDockerfile .
