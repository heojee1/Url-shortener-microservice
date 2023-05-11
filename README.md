**NOTE** | The code for user management and URL shortener services (**/docker/user** and **/docker/url**) is based on the barebone project provided by the instructors of the course Web Services and Cloud-Based Systems.

# Assignment 3.1 - Docker

## File Structure
```
.
├── docker
│   ├── db
│       └── init.sql
│   ├── user
│       ├── .env
│       ├── app.py
│       ├── utils.py
│       ├── Dockerfile
│       └── requirements.txt
│   ├── url
│       ├── .env
│       ├── app.py
│       ├── utils.py
│       ├── **Dockerfile**
│       └── requirements.txt
│   ├── nginx
│       ├── Dockerfile
│       └── nginx.conf
└── kube
```

## Starting the services
```bash
# Setup the virtual environment locally
cd docker
docker compose up -d
```
You can now access both user management and URL shortener service via localhost.

## Using the services
Access user management service with prefix ```localhost/users``` and URL shortener service with prefix ```localhost/```.
For instance send a POST request to ```localhost/users/login``` for login and a POST request to ```localhost/``` to create a new short URL.

## Removing the services
Bring down the docker containers.
```bash
docker compose down
```

# Assignment 3.2 - Kubernetes

## File Structure
```
.
├── kube
│   ├── db
│       ├── postgres-config.yaml
│       ├── postgres-secret.yaml
│       ├── postgres-storage.yaml
│       ├── postgres-service.yaml
│       ├── postgres-network.yaml
│       └── postgres-deployment.txt
│   ├── user
│       ├── api-config.yaml
│       ├── api-service.yaml
│       └── api-deployment.txt
│   ├── url
│       ├── api-config.yaml
│       ├── api-service.yaml
│       └── api-deployment.txt
└── docker
```

## Accessing VM
We are using virtual machines 187, 188, and 189 provided.
We set 189 as a control pane and 187 and 188 as worker nodes.

```bash
ssh student189@145.100.135.189 
```
Put in ```changeme``` as the password when prompted.

## Starting the service
The kubernetes files are under folder 18_web_service_3/kube
Under this folder, there are folders **user**, **url**, and **db**, each containing relevant kubernetes files for user manangment, URL shortener, and database.

Apply the files as follows:
```bash
# Navigate to the folder with kubernetes files
cd 18_web_service_3/kube

# Apply the kubernetes files for each services
kubectl apply -f db
kubectl apply -f user
kubectl apply -f url
```

It will create 1 pod for PostgreSQL, 1 pod for user management, and 3 pods for URL shortener.
Please wait until all the pods are up and running.
You may monitor the status using the command:
```bash
kubectl get pods -n shortener-app
```

## Using the services
You may access the services from local machines via NodePort.
The user management service is accessible via ```30003``` and URL shortener service via ```30002```.
You can use the IP address of any of the three VMs (187, 188, 189) along with the ports.

For instance:
* access user management service through ```http://145.100.135.189:30003/users```
* access URL shortener service through ```http://145.100.135.189:30002/url```

## Removing the service
```bash
# Delete the kubernetes files for each services
kubectl delete -f db
kubectl delete -f user
kubectl delete -f url
```
