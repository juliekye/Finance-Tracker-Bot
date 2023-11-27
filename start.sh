#!/usr/bin/env bash

# Create necessary folders
mkdir -p storage/logs/ 

# Source environment variables
set -a 
source .docker/.env
set +a

# Initialize build variable as empty
build=""

# Check if --build is passed
if [[ $1 == "--build" ]]; then
  build="--build"
fi


# Start a dev environment
echo "Select the dev environment to start:"
echo "0) Start containers in production mode"
echo "1) 2FA Bot"
echo "2) Finance Bot"
read -p "Enter your choice here: (0 - 2): " choice

case $choice in
    0)
        echo "Starting containers in production mode..."
        docker compose -p ${PROJECT_NAME}  -f .docker/docker-compose.yml up  ${build} -d
        ;;
    1)
        echo "Starting 2FA Bot dev environment..."
        docker compose -p ${PROJECT_NAME} -f .docker/docker-compose.yml -f .docker/dev-env/docker-compose.2fa.dev.yml up  ${build} -d
        ;;
    2)
        echo "Starting Finance Bot dev environment..."
        docker compose -p ${PROJECT_NAME} -f .docker/docker-compose.yml -f .docker/dev-env/docker-compose.finance.dev.yml up ${build} -d
        ;;
    *)
        echo "Invalid choice..."
        ;;
esac
