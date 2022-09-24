Download from Google Disk users_db-image.zip

!!!! if not working as is - install Docker Desktop !!!!
install Docker Desktop on Windows (before enable Hyper V in add/remove Windows components,
 Virtual Machine Platform and Windows Subsystem for Linux -
 https://stackoverflow.com/questions/66267529/docker-desktop-3-1-0-installation-issue-access-is-denied
 )
run docker desktop from start menu
!!!!!


!!!!!!!!!!!!! Use container !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
On server load and run:
docker load -i users_db-image.zip

!!!! her change path from "e:\" to where datadase file should be stored
docker run -d -p 8000:5000 -v e:\:/backend/db_media --name users_db-service users_db-service:v0.1.0


Stop service:
docker stop users_db-service

Remove service:
docker rm -f users_db-service
docker rmi --force users_db-service:v0.1.0


!!!!!!!!!!!!! For dev - build and deploy !!!!!!!!!!!!!!!!
Build container:
docker build -t users_db-service:v0.1.0 backend/

run container:
docker run -d -p 8000:5000 -v e:\:/backend/db_media --name users_db-service users_db-service:v0.1.0

stop container:
docker stop users_db-service
docker rm -f users_db-service

remove container:
docker rmi --force users_db-service:v0.1.0

Save to file
docker save -o users_db-image.zip users_db-service
