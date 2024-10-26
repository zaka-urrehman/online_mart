# Online Mart Backend Solution

This repository contains a complete backend solution for an **Online Mart**, built using an **event-driven microservices architecture**. The system is designed to be scalable, reliable, and efficient, using independent microservices that communicate asynchronously.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Microservices](#microservices)
- [Tools and Technologies](#tools-and-technologies)
- [Setup Instructions](#setup-instructions)
- [Running the Project](#running-the-project)
- [Authentication and Security](#authentication-and-security)
- [Event Handling](#event-handling)
- [Payment Integration](#payment-integration)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## Overview
The backend system of the **Online Mart** manages user authentication, product management, order processing, inventory updates, notifications, and payments. Each service operates independently and communicates asynchronously using **Kafka**. The project is built with **Python, FastAPI, SqlModel**, and other modern tools.

## Architecture
The system is designed using **microservices architecture** with each service focusing on a specific domain:
1. **User Service**: Handles user authentication, registration, and profiles.
2. **Product Service**: Manages product catalog and CRUD operations.
3. **Order Service**: Processes orders and manages their statuses.
4. **Inventory Service**: Tracks and updates product inventory.
5. **Notification Service**: Sends user notifications (e.g., email, SMS).
6. **Payment Service**: Integrates with **Stripe** for payment processing.

The services are connected via **Kafka** for asynchronous communication, while **Kong** serves as the API Gateway for secure access.

## Tools and Technologies
- **Backend Framework**: Python, FastAPI, SqlModel
- **Containerization**: Docker, Docker Compose
- **Database**: PostgreSQL
- **Event Broker**: Kafka
- **API Gateway & Load Balancer**: Kong
- **Payment Integration**: Stripe
- **Serialization**: Protocol Buffers
- **Authentication**: JWT

## Setup Instructions
To run this project locally, you must have:
- **Docker Desktop** installed (along with WSL on Windows)
- Or **Docker** installed on **Linux**

### Initial Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/zaka-urrehman/online_mart.git
   cd online_mart

2. **Set up Environment Variables:**
    - Set the necessary variables like USER_SECRET_KEY, DATABASE_URL, STRIPE_API_KEY, etc
3. **Start Docker Containers:**
    - Run the following command to start all services
   ```bash
   docker-compose up --build
   ```
   All Containers must set up automatically. You don't have to do it manually.
Once all the services are up, you can run the project by the following steps.

### Running the Project
### 1. Verify Kong Configuration
- Once the containers are running, Kong's configuration will be set up automatically.
- To verify:
  1. Open your browser and navigate to `http://localhost:8003`.
  2. You can verify routes and gateway services here for each container.
### 2. Set up JWT Authentication for User-Service
- Ensure JWT authentication is properly configured:
  1. Go to [Kong Admin UI](http://localhost:8003) (or appropriate port for Kong).
  2. In the **Consumers** tab, select the consumer created for the user-service (should be created automatically).
  3. If not present, create a new consumer with a username (e.g., `example_user`) and add JWT credentials for that consumer. Your credentials for consumer and your USER_SERCRET_KEY in your .env file in user-service should be same.
  4. Copy the **Credential ID** of the consumer.
  5. Update the `.env` file in the **user-service** with this Credential ID under `ISS`.

  Once updated, restart the **user-service** to apply the changes:
  ```bash
  docker-compose restart user-service
  ```
### 3. Set up Stripe for Payment Service
- To enable payment processing:
  1. Copy your **Stripe API key** and paste it in the `.env` file as `STRIPE_API_KEY`.
  2. Once the containers are running, view the logs of the **Stripe CLI container** to retrieve the **webhook secret**:
     ```bash
     docker logs -f stripe-cli
     ```
  If you don't find the webhook secret, it might be because the container haven't picked up 
  the env for stripe API key. You can restart the container and you will see your webhook 
  secret.

  3. Copy the displayed **webhook secret** and update the `.env` file of the **payment-service** with `WEBHOOK_SECRET`.
  4. Restart the **payment-service** container to apply the changes:
     ```bash
     docker-compose restart payment-service
     ```

### 4. Test the Microservices and APIs

1. **Access the FastAPI documentation:**
   Go to the following URLs in your browser to access the API documentation (Swagger UI) for each service:
   - **User Service:** [http://localhost:8000/user-service/docs](http://localhost:8000/user-service/docs)
   - **Product Service:** [http://localhost:8000/product-service/docs](http://localhost:8000/product-service/docs)
   - **Order Service:** [http://localhost:8000/inventory-service/docs](http://localhost:8000/inventory-service/docs)
   - **Inventory Service:** [http://localhost:8000/order-service/docs](http://localhost:8000/order-service/docs)


2. **Test authentication:**
   - Under the **user-service** Use the **add-user endpoint** to add a user and **add address endpoint** to add address for user which will later be used for placing order.
   - Use the **login endpoint** of the User Service to generate a JWT token.
   - Copy the token and use it as the **Authorization header** in the subsequent service requests.
2. **Add a Product:**
   - Add a Category, Size and then a product. 
   - Use the **Admin Account** for this purpose as only admin can do these operations on products etc. You can create an Admin account by navigating to the **add-admin** endpoint under the **user-service**.


3. **Place an order:**
   - Add a product to cart under the **order-service**.
   - Use the **Create Order** endpoint in the Order Service to place a new order.
   - This triggers payment processing via Stripe and updates the order status upon successful payment.

4. **Check inventory:**
   - Use the Inventory Service endpoints to increase, decrease, or set product quantities.
   - Use only **admin account** as user account will be restricted from inventory-service.


5. **Review Kafka events:**
   - Check Kafka UI at [http://localhost:9080](http://localhost:9080) to monitor event topics and messages exchanged between services.

This completes the testing of all microservices.

### 5. Stopping the Services

To stop all running containers and services:

1. Run the following command:
   ```bash
   docker compose down
   ```
### 6. Troubleshooting Tips

- **Issue:** Services not starting as expected.
  - **Solution:** Ensure Docker Desktop or Docker is running correctly, and try using `docker compose up --build` to rebuild the images.

- **Issue:** JWT verification fails even after a token is generated.
  - **Solution:** Verify the JWT token's `iss` claim is set correctly, matching the Kong consumer ID.

- **Issue:** Payment Service is not processing payments.
  - **Solution:** Ensure that the Stripe webhook secret is set correctly in the Payment Service’s `.env` file.

- **Issue:** Kafka messages not being consumed.
  - **Solution:** Restart the services depending on Kafka, especially the consumers, to ensure proper connectivity.

### Final Note

You’ve successfully set up the backend for the Online Mart application. This project showcases an event-driven microservices architecture with secure authentication and payment processing. For any adjustments or extensions, refer to the codebase and documentation. Thank you for trying it out!



