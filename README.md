**NOTE** | The code for user management and URL shortener services (**/docker/user and **/docker/url**) is based on the barebone project provided by the instructors of the course Web Services and Cloud-Based Systems.

# Assignment 3.1 - Docker

## Usage
### Starting the services
```bash
# Setup the virtual environment locally
cd docker
docker compose up -d
```
You can now access both user management and URL shortener service via localhost.

### Using the services
Access user management service with prefix ```localhost/users``` and URL shortener service with prefix ```localhost/```.
For instance send a POST request to ```localhost/users/login``` for login and a POST request to ```localhost/``` to create a new short URL.
