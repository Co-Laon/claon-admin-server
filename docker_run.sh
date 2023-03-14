db_image_name="claon_admin"
db_container_name="claon_admin_container"
port=8000

echo "## Pull code ##"
git pull origin main

echo "## Automation docker-database build and run ##"

# remove container
echo "=> Remove previous container..."
docker rm -f ${db_container_name}

# remove image
echo "=> Remove previous image..."
docker rmi -f ${db_image_name}

# new-build/re-build docker image
echo "=> Build new image..."
docker build --tag ${db_image_name} .

# Run container
echo "=> Run container..."
docker run -d -p ${port}:${port} --name ${db_container_name} ${db_image_name}
