from sqlmodel import Session, select
from app.db.db_connection import DB_SESSION
from app.models.product_models import Product

def modify_product_quantity(product_id: int, quantity: int, type: str, session: DB_SESSION):
    # Fetch the product from the database using session.exec
    statement = select(Product).where(Product.product_id == product_id)
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