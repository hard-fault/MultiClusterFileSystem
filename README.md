# Multi Cluster File System

## System Architecture
![Alt text](https://github.com/hard-fault/MultiClusterFileSystem/blob/master/rsrc/arch.png)

### Setting up the container infrastructure

1. Install docker CE (https://docs.docker.com/v17.12/install/)
2. Clone the repository (https://github.com/hard-fault/MultiClusterFileSystem.git)
3. Pull the docker image for containers 
```sh
docker pull shrey67/node_image
```
4. Specify the topology in 
```sh
MultiClusterFileSystem/infra/config/config.json
```
5. Deploy containers
```sh
cd MultiClusterFileSystem/infra/setup/
python setup.py
```
6. List all the containers
```sh
docker ps
```
7. View container network topology and their IPs.
```sh
cd MultiClusterFileSystem/output/
cat ip.json
```
8. Copy a file to container
```sh
docker cp <container_name> local_file_path <container_name>:destination_path
```
9. Login to a container
```sh
docker exec -it <container_name> /bin/bash
```
10. Remove the setup
```sh
cd MultiClusterFileSystem/infra/setup
python setup.py -d
```
