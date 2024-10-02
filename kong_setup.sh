#!/bin/sh

echo "Starting Kong setup script..."

# Check if .env file exists and load environment variables
if [ -f .env ]; then
    set -a
    . ./.env
    set +a
    echo ".env file loaded successfully"
else
    echo ".env file not found"
fi

# Define Kong admin URL
KONG_ADMIN_URL="http://host.docker.internal:8001"
echo "KONG_ADMIN_URL set to $KONG_ADMIN_URL"

# Wait for Kong to be ready
echo "Waiting for Kong to be ready..."
until curl --output /dev/null --silent --head --fail $KONG_ADMIN_URL; do
    printf '.'
    sleep 5
done

echo "\nKong is ready!"

# Check if user-service exists
echo "Checking if user-service exists..."
service_check=$(curl -s $KONG_ADMIN_URL/services/user-service)

if echo "$service_check" | grep -q '"name":"user-service"'; then
    echo "user-service already exists. Skipping service creation."
else
    # Create user-service in Kong
    echo "Creating user-service..."
    curl -i -X POST $KONG_ADMIN_URL/services \
      --data name=user-service \
      --data url='http://user-service:8000'  # Assuming user-service runs at port 8000 inside your network

    # Check if service was created successfully
    if [ $? -eq 0 ]; then
        echo "user-service created successfully!"
    else
        echo "Failed to create user-service"
        exit 1
    fi
fi

# Check if a route for user-service already exists
echo "Checking if route for user-service exists..."
route_check=$(curl -s $KONG_ADMIN_URL/routes)

if echo "$route_check" | grep -q '"paths":["/users"]'; then
    echo "Route for /users already exists. Skipping route creation."
else
    # Add a route for user-service
    echo "Adding a route for user-service..."
    curl -i -X POST $KONG_ADMIN_URL/routes \
      --data 'paths[]=/users' \
      --data service.name=user-service

    # Check if route was added successfully
    if [ $? -eq 0 ]; then
        echo "Route for user-service added successfully!"
    else
        echo "Failed to add route for user-service"
        exit 1
    fi
fi

echo "Kong configuration completed!"
