import json

from sqlalchemy.orm import Session
from typing import Any, Annotated
from fastapi import HTTPException, status, Header
from datetime import datetime, timezone
from sqlalchemy import select
from aiokafka import AIOKafkaProducer

from app.models.order_models import Order, OrderProducts, OrderCreate, OrderStatusUpdate
from app.db.db_connection import DB_SESSION, engine
from app.kafka.producer import KAFKA_PRODUCER
from app.settings import KAFKA_ORDER_TOPIC
from app.utils.auth import get_user_id_from_token
from app.protobuf import order_pb2


# ========================== CREATE ORDER ==========================

async def create_order(order_data: OrderCreate, session: DB_SESSION, producer: KAFKA_PRODUCER, authorization: Annotated[str, Header()]):
    # print("Step 1: Start create_order")
    user_id = get_user_id_from_token(authorization)   

    if user_id != order_data.user_id:
        raise HTTPException(status_code=404, detail="Invalid User ID provided")

    # Step 2: Validate products and calculate total amount
    total_amount = 0
    for product_item in order_data.products:
        # product_row = session.exec(select(Product).where(Product.product_id == product_item.product_id)).first()
        # # print(f"Step 3: Retrieved product row: {product_row}")

        # # Directly extract the Product instance from the tuple
        # product = product_row[0]
        

        # # Ensure the extracted instance is of Product type
        # if not isinstance(product, Product):
        #     # print("Product is not a Product instance")
        #     raise HTTPException(status_code=500, detail="Product data is not in the expected format")

        # if isinstance(product, Product):
        #     price = product.price            
        # # Extract and check product price
        # # price = product.price
        # if price is None:
        #     raise HTTPException(status_code=404, detail="Product price not found")

        # # print(f"Step 3a: Product price: {price}")

        # # Validate size
        # size = session.exec(select(Size).where(Size.size_id == product_item.size_id)).first()
        # # print(f"Step 4: Retrieved size: {size}")
        # if not size:
        #     raise HTTPException(status_code=404, detail=f"Size with ID {product_item.size_id} not found")

        # Check product price and update total_amount
        if product_item.product_price > 0:
            total_amount += product_item.product_price * product_item.quantity
            # print(f"Step 4a: Total amount updated to {total_amount}")
        else:
            print(f"Product ID {product_item.product_id} has a price of 0. Skipping price calculation.")

    # Calculate net amount (total - discount)
    discount = order_data.discount if order_data.discount else 0.0
    net_amount = total_amount - discount
    # print(f"Total Amount: {total_amount}, Discount: {discount}, Net Amount: {net_amount}")

    # Step 3: Create the order
    new_order = Order(
        user_id=order_data.user_id,
        delivery_address=order_data.delivery_address,
        nearest_branch=order_data.nearest_branch,
        order_status='pending',
        payment_status='unpaid',
        total_amount=total_amount,
        discount=discount,
        net_amount=net_amount,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(new_order)
    session.commit()
    session.refresh(new_order)
    # print(f"Order created successfully with order_id: {new_order.order_id}")

    # Step 4: Insert products into OrderProducts
    for product_item in order_data.products:
        order_product = OrderProducts(
            order_id=new_order.order_id,
            product_id=product_item.product_id,
            price_at_purchase=product_item.product_price,
            quantity=product_item.quantity
        )
        session.add(order_product)

    # Step 5: Commit final changes to the database
    session.commit()
    # print("All products added to order and committed to database")

    # Step 6: Send order data to Kafka topic
    await send_order_to_kafka(producer, KAFKA_ORDER_TOPIC, new_order, order_data.user_email)

    return {
        "message": "Order created successfully",
        "order_id": new_order.order_id
    }


# ========================== SEND MESSAGE TO KAFKA TOPIC (order added to db with payment_status="unpaid") ==========================


async def send_order_to_kafka(producer: AIOKafkaProducer, topic: str, order_data: Any, email: str):
    """
    Send order data to Kafka topic.

    Args:
        producer (AIOKafkaProducer): Kafka producer instance.
        topic (str): Kafka topic name.
        order_data (dict): Order data.
    """

    # Add the necessary fields for payment processing
    # message = {
    # "order_id": order_data.order_id,
    # "user_id": order_data.user_id,
    # "user_email": email,
    # "delivery_address": order_data.delivery_address,
    # "total_amount": order_data.total_amount,
    # "discount": order_data.discount,
    # "net_amount": order_data.net_amount,
    # "order_status": order_data.order_status,
    # "payment_status": order_data.payment_status,
    # # "created_at": order_data.created_at,
    # "metadata": {
    #     "payment_intent": "create",
    #     "email": email  # Required for communication or confirmation
    #     }
    # }
    # Create an Order message instance
    # Convert order_id and user_id to strings
    order_message = order_pb2.Order(
        order_id=str(order_data.order_id),  # Convert to string
        user_id=str(order_data.user_id),    # Convert to string
        user_email=email,
        delivery_address=str(order_data.delivery_address),
        total_amount=float(order_data.total_amount),
        discount=float(order_data.discount),
        net_amount=float(order_data.net_amount),
        order_status=order_data.order_status,
        payment_status=order_data.payment_status,
        metadata=order_pb2.Metadata(
            payment_intent="create",
            email=email
        )
    )

    try:
        # # Serialize the message to JSON format
        # message_bytes = json.dumps(message).encode("utf-8")

         # Serialize the message to Protobuf format
        message_bytes = order_message.SerializeToString()
        
        # Send the message to the specified Kafka topic
        await producer.send_and_wait(topic, message_bytes)

        print(f"Order data sent to Kafka topic '{topic}': {message_bytes}")
    except Exception as e:
        print(f"Failed to send order data to Kafka: {str(e)}") 




# ========================== GET ORDER BY ID WITH PRODUCTS ==========================

def get_order_by_id(order_id: int, session: DB_SESSION):
    """
    Fetch an order by ID and include its products in the response.
    
    Args:
        order_id (int): ID of the order.
        session (Session): Database session.

    Returns:
        dict: Order details along with products.
    """
    # Step 1: Fetch the order with products using a join
    order_data = session.exec(
        select(Order, OrderProducts)
        .join(OrderProducts, Order.order_id == OrderProducts.order_id)       
        .where(Order.order_id == order_id)
    ).all()

    if not order_data:
        raise HTTPException(status_code=404, detail="Order not found")

    # Extract order details and products
    order_info = order_data[0][0]  # Get order details from the first tuple
    products = [
        {
            "product_id": op.product_id,
            "quantity": op.quantity,            
            "price_at_purchase": op.price_at_purchase,
        }
        for _, op in order_data
    ]

    return {
        "order_id": order_info.order_id,
        "user_id": order_info.user_id,
        "delivery_address": order_info.delivery_address,
        # "nearest_branch": order_info.nearest_branch,
        "order_status": order_info.order_status,
        "payment_status": order_info.payment_status,
        "total_amount": order_info.total_amount,
        "discount": order_info.discount,
        "net_amount": order_info.net_amount,
        "created_at": order_info.created_at,
        "updated_at": order_info.updated_at,
        "products": products
    }

# ========================== GET ALL ORDERS WITH PRODUCTS ==========================

def get_all_orders( session: DB_SESSION,  authorization: Annotated[str, Header()]):
    user_id = get_user_id_from_token(authorization)

    """
    Fetch all orders of a user and include their products in the response.
    
    Args:
        user_id (int): ID of the user.
        session (Session): Database session.

    Returns:
        list: List of orders with products.
    """
    # Step 1: Fetch all orders of a user with products using a join
    order_data = session.exec(
        select(Order, OrderProducts)
        .join(OrderProducts, Order.order_id == OrderProducts.order_id)        
        .where(Order.user_id == user_id)
    ).all()

    if not order_data:
        raise HTTPException(status_code=404, detail="No orders found")

    # Step 2: Group products by orders
    grouped_orders = {}
    for order, op in order_data:
        if order.order_id not in grouped_orders:
            grouped_orders[order.order_id] = {
                "order_id": order.order_id,
                "user_id": order.user_id,
                "delivery_address": order.delivery_address,
                # "nearest_branch": order.nearest_branch,
                "order_status": order.order_status,
                "payment_status": order.payment_status,
                "total_amount": order.total_amount,
                "discount": order.discount,
                "net_amount": order.net_amount,
                "created_at": order.created_at,
                "updated_at": order.updated_at,
                "products": []
            }
        
        grouped_orders[order.order_id]["products"].append({
            "product_id": op.product_id,
            "quantity": op.quantity,
            "price_at_purchase": op.price_at_purchase            
        })

    return list(grouped_orders.values())

# ========================== UPDATE ORDER STATUS ==========================

def update_order_status(order_id: int, status_update: OrderStatusUpdate, session: DB_SESSION):
    """
    Updates the order status for a given order.
    """
    order = session.get(Order, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update order status and timestamp
    order.order_status = status_update.order_status
    order.updated_at = datetime.now(timezone.utc)

    session.add(order)
    session.commit()

    return {"message": "Order status updated successfully"}

# ========================== DELETE ORDER ==========================

def delete_order(order_id: int, session: DB_SESSION):
    """
    Deletes all associated order products and then deletes the order.
    """
    # Step 1: Check if the order exists
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Step 2: Fetch and delete all order products related to the order
    order_products_retrieved = session.exec(
        select(OrderProducts).where(OrderProducts.order_id == order_id)
    ).all()

    order_products = order_products_retrieved[0]

    for order_product in order_products:
        # Use session.get() to delete each OrderProducts record
        order_product_to_delete = session.get(
            OrderProducts, 
            (order_product.order_id, order_product.product_id)
        )
        if order_product_to_delete:
            session.delete(order_product_to_delete)

    # Step 3: Delete the order
    session.delete(order)
    session.commit()

    return {"message": "Order and associated products deleted successfully"}


# ========================= UPDATE PAYMENT STATUS FOR AN ORDER ==================
def update_payment_status(order_id: int, status_update: str):
    """
    Updates the payment status for a given order.
    """
   
    with Session(engine) as session:

        order = session.get(Order, order_id)

        if not order:
          raise HTTPException(status_code=404, detail="Order not found")

     # Update order status and timestamp
        order.payment_status = status_update
        order.updated_at = datetime.now(timezone.utc)

        session.commit()

    return {"message": "Order status updated successfully"}
