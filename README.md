**NOTE** | The code for user management and URL shortener services (**/docker/user and **/docker/url**) is based on the barebone project provided by the instructors of the course Web Services and Cloud-Based Systems.

# Assignment 3.1 - Docker

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

# Assignment 3.2 - Kubernetes

## Accessing VM
We are using virtual machines 187, 188, and 189 provided.
We set 189 as a control pane and 187 and 188 as worker nodes.

```bash
ssh student189@145.100.135.189 
```
Put in ```changeme``` as the password when prompted.

## Starting the service
The kubernetes files are under folder web/kube
Under this folder, there are folders **user**, **url**, and **db**, each containing relevant kubernetes files for user manangment, URL shortener, and database.

Apply the files as follows:
```bash
# Navigate to the folder with kubernetes files
cd web/kube

# Apply the kubernetes files for each services
kubectl apply -f db
kubectl apply -f user
kubectl apply -f url
```

## Using the services
You may access the services from local machines via NodePort.
The user management service is accessible via ```30003``` and URL shortener service via ```30002```.
You can use the IP address of any of the three VMs (187, 188, 189) along with the ports.

For instance:
* access user management service through ```http://145.100.135.189:30003/users```
* access URL shortener service through ```http://145.100.135.189:30002/url```

