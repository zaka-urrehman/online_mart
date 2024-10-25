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

# ----------------------------------------
# Check if user-service exists
# ----------------------------------------
echo "Checking if user-service exists..."
service_check=$(curl -s $KONG_ADMIN_URL/services/user-service)

if echo "$service_check" | grep -q '"name":"user-service"'; then
    echo "user-service already exists. Skipping service creation."
else
    # Create user-service in Kong
    echo "Creating user-service..."
    curl -i -X POST $KONG_ADMIN_URL/services \
      --data name=user-service \
      --data url='http://host.docker.internal:8010'  # Assuming user-service runs at port 8000

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
route_check=$(curl -s $KONG_ADMIN_URL/routes | jq '.data[] | select(.paths[] == "/user-service")')

if [ -n "$route_check" ]; then
    echo "Route for /user-service already exists. Skipping route creation."
else
    # Add a route for user-service
    echo "Adding a route for user-service..."
    curl -i -X POST $KONG_ADMIN_URL/routes \
      --data 'paths[]=/user-service' \
      --data service.name=user-service

    # Check if route was added successfully
    if [ $? -eq 0 ]; then
        echo "Route for user-service added successfully!"
    else
        echo "Failed to add route for user-service"
        exit 1
    fi
fi

# ----------------------------------------
# Check if product-service exists
# ----------------------------------------
echo "Checking if product-service exists..."
product_service_check=$(curl -s $KONG_ADMIN_URL/services/product-service)

if echo "$product_service_check" | grep -q '"name":"product-service"'; then
    echo "product-service already exists. Skipping service creation."
else
    # Create product-service in Kong
    echo "Creating product-service..."
    curl -i -X POST $KONG_ADMIN_URL/services \
      --data name=product-service \
      --data url='http://host.docker.internal:8011'  # Assuming product-service runs at port 8011

    # Check if service was created successfully
    if [ $? -eq 0 ]; then
        echo "product-service created successfully!"
    else
        echo "Failed to create product-service"
        exit 1
    fi
fi

# Check if a route for product-service already exists
echo "Checking if route for product-service exists..."
product_route_check=$(curl -s $KONG_ADMIN_URL/routes | jq '.data[] | select(.paths[] == "/product-service")')

if [ -n "$product_route_check" ]; then
    echo "Route for /product-service already exists. Skipping route creation."
else
    # Add a route for product-service
    echo "Adding a route for product-service..."
    curl -i -X POST $KONG_ADMIN_URL/routes \
      --data 'paths[]=/product-service' \
      --data service.name=product-service

    # Check if route was added successfully
    if [ $? -eq 0 ]; then
        echo "Route for product-service added successfully!"
    else
        echo "Failed to add route for product-service"
        exit 1
    fi
fi

# ----------------------------------------
# Check if inventory-service exists
# ----------------------------------------
echo "Checking if inventory-service exists..."
inventory_service_check=$(curl -s $KONG_ADMIN_URL/services/inventory-service)

if echo "$inventory_service_check" | grep -q '"name":"inventory-service"'; then
    echo "inventory-service already exists. Skipping service creation."
else
    # Create inventory-service in Kong
    echo "Creating inventory-service..."
    curl -i -X POST $KONG_ADMIN_URL/services \
      --data name=inventory-service \
      --data url='http://host.docker.internal:8012'  # Assuming inventory-service runs at port 8012

    # Check if service was created successfully
    if [ $? -eq 0 ]; then
        echo "inventory-service created successfully!"
    else
        echo "Failed to create inventory-service"
        exit 1
    fi
fi

# Check if a route for inventory-service already exists
echo "Checking if route for inventory-service exists..."
inventory_route_check=$(curl -s $KONG_ADMIN_URL/routes | jq '.data[] | select(.paths[] == "/inventory-service")')

if [ -n "$inventory_route_check" ]; then
    echo "Route for /inventory-service already exists. Skipping route creation."
else
    # Add a route for inventory-service
    echo "Adding a route for inventory-service..."
    curl -i -X POST $KONG_ADMIN_URL/routes \
      --data 'paths[]=/inventory-service' \
      --data service.name=inventory-service

    # Check if route was added successfully
    if [ $? -eq 0 ]; then
        echo "Route for inventory-service added successfully!"
    else
        echo "Failed to add route for inventory-service"
        exit 1
    fi
fi



# ----------------------------------------
# Check if notification-service exists
# ----------------------------------------
echo "Checking if notification-service exists..."
notification_service_check=$(curl -s $KONG_ADMIN_URL/services/notification-service)

if echo "$notification_service_check" | grep -q '"name":"notification-service"'; then
    echo "notification-service already exists. Skipping service creation."
else
    # Create notification-service in Kong
    echo "Creating notification-service..."
    curl -i -X POST $KONG_ADMIN_URL/services \
      --data name=notification-service \
      --data url='http://host.docker.internal:8013'  # Assuming notification-service runs at port 8013

    # Check if service was created successfully
    if [ $? -eq 0 ]; then
        echo "notification-service created successfully!"
    else
        echo "Failed to create notification-service"
        exit 1
    fi
fi

# Check if a route for notification-service already exists
echo "Checking if route for notification-service exists..."
notification_route_check=$(curl -s $KONG_ADMIN_URL/routes | jq '.data[] | select(.paths[] == "/notification-service")')

if [ -n "$notification_route_check" ]; then
    echo "Route for /notification-service already exists. Skipping route creation."
else
    # Add a route for notification-service
    echo "Adding a route for notification-service..."
    curl -i -X POST $KONG_ADMIN_URL/routes \
      --data 'paths[]=/notification-service' \
      --data service.name=notification-service

    # Check if route was added successfully
    if [ $? -eq 0 ]; then
        echo "Route for notification-service added successfully!"
    else
        echo "Failed to add route for notification-service"
        exit 1
    fi
fi




# ----------------------------------------
# Add the Order Service
# ----------------------------------------
echo "Checking if order-service exists..."
order_service_check=$(curl -s $KONG_ADMIN_URL/services/order-service)

if echo "$order_service_check" | grep -q '"name":"order-service"'; then
    echo "order-service already exists. Skipping service creation."
else
    echo "Creating order-service..."
    curl -i -X POST $KONG_ADMIN_URL/services \
      --data name=order-service \
      --data url='http://host.docker.internal:8014'  # Assuming order-service runs at port 8014

    if [ $? -eq 0 ]; then
        echo "order-service created successfully!"
    else
        echo "Failed to create order-service"
        exit 1
    fi
fi

echo "Checking if route for order-service exists..."
order_route_check=$(curl -s $KONG_ADMIN_URL/routes | jq '.data[] | select(.paths[] == "/order-service")')

if [ -n "$order_route_check" ]; then
    echo "Route for /order-service already exists. Skipping route creation."
else
    echo "Adding a route for order-service..."
    curl -i -X POST $KONG_ADMIN_URL/routes \
      --data 'paths[]=/order-service' \
      --data service.name=order-service

    if [ $? -eq 0 ]; then
        echo "Route for order-service added successfully!"
    else
        echo "Failed to add route for order-service"
        exit 1
    fi
fi




# ----------------------------------------
# Add the Payment Service
# ----------------------------------------
echo "Checking if payment-service exists..."
payment_service_check=$(curl -s $KONG_ADMIN_URL/services/payment-service)

if echo "$payment_service_check" | grep -q '"name":"payment-service"'; then
    echo "payment-service already exists. Skipping service creation."
else
    echo "Creating payment-service..."
    curl -i -X POST $KONG_ADMIN_URL/services \
      --data name=payment-service \
      --data url='http://host.docker.internal:8015'  # Payment-service port

    if [ $? -eq 0 ]; then
        echo "payment-service created successfully!"
    else
        echo "Failed to create payment-service"
        exit 1
    fi
fi

echo "Checking if route for payment-service exists..."
payment_route_check=$(curl -s $KONG_ADMIN_URL/routes | jq '.data[] | select(.paths[] == "/payment-service")')

if [ -n "$payment_route_check" ]; then
    echo "Route for /payment-service already exists. Skipping route creation."
else
    echo "Adding a route for payment-service..."
    curl -i -X POST $KONG_ADMIN_URL/routes \
      --data 'paths[]=/payment-service' \
      --data service.name=payment-service

    if [ $? -eq 0 ]; then
        echo "Route for payment-service added successfully!"
    else
        echo "Failed to add route for payment-service"
        exit 1
    fi
fi




# -------------------------------------
# JWT Plugin
# ------------------------------------

# Define variables
CONSUMER_NAME="example_user"
SECRET_KEY="this is secret key for user"

# Check if the consumer already exists
consumer_check=$(curl -s -o /dev/null -w "%{http_code}" $KONG_ADMIN_URL/consumers/$CONSUMER_NAME)

if [ "$consumer_check" -ne 200 ]; then
    echo "Creating consumer: $CONSUMER_NAME"
    curl -i -X POST $KONG_ADMIN_URL/consumers/ \
        --data "username=$CONSUMER_NAME"
else
    echo "Consumer $CONSUMER_NAME already exists."
fi

# Check if JWT credentials already exist for the consumer
jwt_check=$(curl -s $KONG_ADMIN_URL/consumers/$CONSUMER_NAME/jwt)

if echo "$jwt_check" | grep -q "$SECRET_KEY"; then
    echo "JWT credentials already exist for consumer: $CONSUMER_NAME"
else
    echo "Creating JWT credentials for consumer: $CONSUMER_NAME"
    curl -i -X POST $KONG_ADMIN_URL/consumers/$CONSUMER_NAME/jwt \
        --data "secret=$SECRET_KEY"
fi

# Enable JWT plugin for inventory-service
plugin_check_inventory=$(curl -s $KONG_ADMIN_URL/services/inventory-service/plugins)
if ! echo "$plugin_check_inventory" | grep -q '"name":"jwt"'; then
    echo "Enabling JWT plugin for inventory-service"
    curl -i -X POST $KONG_ADMIN_URL/services/inventory-service/plugins \
        --data "name=jwt"
else
    echo "JWT plugin already enabled for inventory-service"
fi

# Enable JWT plugin for order-service
plugin_check_order=$(curl -s $KONG_ADMIN_URL/services/order-service/plugins)
if ! echo "$plugin_check_order" | grep -q '"name":"jwt"'; then
    echo "Enabling JWT plugin for order-service"
    curl -i -X POST $KONG_ADMIN_URL/services/order-service/plugins \
        --data "name=jwt"
else
    echo "JWT plugin already enabled for order-service"
fi




echo "Kong configuration completed!"
