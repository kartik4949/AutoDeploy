# AutoDeploy

## STEPS

### Docker Build
```
# Builds docker images with model requirements if any.
chmod +x build.sh
bash build.sh -r path/to/model/requirements.txt
```

### Docker Compose Start
```
# Starts docker images
chmod +x start.sh
bash start.sh -f path/to/config/file/config.yaml
```
