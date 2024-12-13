from sqlmodel import Session, select
from datetime import datetime, timezone
from app.db.db_connection import DB_SESSION, engine
from app.models.models import Inventory
from sqlalchemy.exc import SQLAlchemyError





def add_new_product_in_inventory(product_id: int, quantity: int, brand: str, price: float, expiry: datetime):
    """
    Add a new entry for a product in inventory db.

    Args:
        product_id (int): The ID of the product to add.
        quantity (int): The quantity of the product to add.
        brand (str): The brand of the product to add.
        price (float): The price of the product to add.
        expiry (datetime): The expiry date of the product to add.
    """
    try:
        with Session(engine) as session:
            new_product = Inventory(
                product_id=product_id,
                quantity=quantity,
                brand=brand,
                price=price,
                expiry=expiry
            )
            session.add(new_product)
            session.commit()
            session.refresh(new_product)
        return new_product
    except SQLAlchemyError as e:
        print(f"Error adding product: {e}")
        return None



def modify_product_quantity(product_id: int, quantity: int, type: str, session: DB_SESSION):
    """
    Modify the quantity of a product in inventory based on the type of arguments provided. 

    Args:
        product_id (int): The ID of the product to modify.
        quantity (int): The quantity to modify the product by.
        type (str): The type of modification to perform. Can be "increase", "decrease", or "set".
    """
    # Fetch the product from the database using session.exec
    statement = select(Inventory).where(Inventory.product_id == product_id)
    product = session.exec(statement).first()

    if not product:
        return {"error": "Product not found"}

    # Modify the quantity based on the type
    if type == "increase":
        product.quantity += quantity
    elif type == "decrease":
        if product.quantity < quantity:
            return {"error": "Not enough stock to decrease"}
        product.quantity -= quantity
    elif type == "set":
        product.quantity = quantity
    else:
        return {"error": "Invalid operation type"}    

    product.updated_at = datetime.now(timezone.utc)

    session.add(product)
    session.commit()
    session.refresh(product)

    return {"message": f"Product quantity {type}d successfully", "product": product}




def increase(product_id: int, quantity: int, session: DB_SESSION):
    return  modify_product_quantity(product_id, quantity, "increase", session)


def decrease(product_id: int, quantity: int, session: DB_SESSION):
    return  modify_product_quantity(product_id, quantity, "decrease", session)

def set(product_id: int, quantity: int, session: DB_SESSION):
    return  modify_product_quantity(product_id, quantity, "set", session)