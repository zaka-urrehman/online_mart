from fastapi import HTTPException, Depends, Header
from typing import Annotated
from sqlmodel import Session, select
from datetime import datetime, timezone

from app.models.order_models import Cart, CartProduct, AddToCart, UpdateCart
from app.db.db_connection import DB_SESSION
from app.utils.auth import  get_user_id_from_token



# ================================ ADD ITEM TO CART ================================

def add_item_to_cart(cart_data: AddToCart, session: DB_SESSION, authorization: Annotated[str, Header()]):
    """
    Adds an item to the cart, updating the Cart and CartProduct tables.
    Args:
        cart_data (AddToCart): Data containing user_id, product_id, quantity, and size_id.
        session (Session): Database session for executing queries.
    Returns:
        str: Confirmation message indicating item added to the cart.
    """
    
    # # Step 1: Validate user_id
    # print(f"Step 1: Validating user_id = {cart_data.user_id}")
    # user = session.exec(select(User).where(User.user_id == cart_data.user_id)).first()
    # if not user:
    #     raise HTTPException(status_code=400, detail="Invalid user ID")

    # # Step 2: Validate product_id
    # print(f"Step 2: Validating product_id = {cart_data.product_id}")
    # product = session.exec(select(Product).where(Product.product_id == cart_data.product_id)).first()
    # if not product:
    #     raise HTTPException(status_code=400, detail="Invalid product ID")

    # # Step 3: Validate size_id
    # print(f"Step 3: Validating size_id = {cart_data.size_id}")
    # size = session.exec(select(Size).where(Size.size_id == cart_data.size_id)).first()
    # if not size:
    #     raise HTTPException(status_code=400, detail="Invalid size ID")

    user_id = get_user_id_from_token(authorization)
    if user_id != cart_data.user_id:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    # Step 4: Check if a cart exists for the user
    print(f"Step 4: Checking for existing cart for user_id = {cart_data.user_id}")
    cart = session.exec(
        select(Cart).where(Cart.user_id == cart_data.user_id)
    ).first()

    # Step 5: If no cart exists, create a new one
    if not cart:
        print("Step 5: No existing cart found, creating a new cart")
        cart = Cart(user_id=cart_data.user_id, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
        session.add(cart)
        session.commit()
        session.refresh(cart)
        print(f"Step 5: New cart created with cart_id = {cart.cart_id}")

    # Step 6: Check if the product with the given size already exists in the cart
    print(f"Step 6: Checking if product {cart_data.product_id}  exists in cart {cart.cart_id}")
    cart_product = session.exec(
        select(CartProduct)
        .where(CartProduct.cart_id == cart.cart_id)
        .where(CartProduct.product_id == cart_data.product_id)
    ).first()

    if cart_product:
        # Step 7: If the product exists, update the quantity
        print(f"Step 7: Product found in cart, updating quantity. Previous quantity = {cart_product.quantity}")
        cart_product.quantity += cart_data.quantity
        cart_product.quantity = max(cart_product.quantity, 1)  # Ensure minimum quantity is 1
        print(f"Step 7: Updated quantity = {cart_product.quantity}")
    else:
        # Step 8: If the product does not exist, create a new CartProduct
        print(f"Step 8: Product not found in cart, creating new CartProduct")
        cart_product = CartProduct(
            cart_id=cart.cart_id,
            product_id=cart_data.product_id,           
            quantity=cart_data.quantity,
            product_price=cart_data.product_price
        )
        session.add(cart_product)
        print("Step 8: New CartProduct added to the cart")

    # Step 9: Commit changes to the database
    print("Step 9: Committing changes to the database")
    session.commit()
    session.refresh(cart_product)

    # Step 10: Update the cart's totals (optional)
    update_cart_totals(cart, session)

    return {"message" : "Item added to cart successfully"}


# ================================ RECALCULATE CART TOTAL AFTER ADDING A PRODUCT AND UPDATE ================================
def update_cart_totals(cart: Cart, session: Session):
    
    """
    Updates the total price and subtotal of the cart based on its products.
    Args:
        cart (Cart): The cart to update.
        session (Session): Database session for executing queries.
    """
    print("Step 11: Updating cart totals")
    cart_products = session.exec(
        select(CartProduct).where(CartProduct.cart_id == cart.cart_id)
    ).all()

    # products_total = sum(cp.quantity * session.exec(
    #     select(Product.price).where(Product.product_id == cp.product_id)
    # ).first() for cp in cart_products)

    products_total = sum(cp.quantity * cp.product_price for cp in cart_products)

    cart.products_total = products_total
    cart.sub_total = products_total + cart.delivery_charges - cart.discount
    cart.updated_at = datetime.now(timezone.utc)

    session.add(cart)
    session.commit()
    print("Step 11: Cart totals updated successfully")

# ================================ GET CART ================================

def get_cart_details(session: DB_SESSION,  authorization: Annotated[str, Header()]):
    """
    Fetches cart details for a given user, including products, sizes, and other cart information.
    
    Args:
        user_id (int): ID of the user whose cart needs to be fetched.
        session (Session): Database session for executing queries.
    
    Returns:
        Dict: Formatted cart details including products, size, and cart info.
    """
    user_id = get_user_id_from_token(authorization)
    # Step 1: Fetch the cart for the user
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if not cart:
        raise HTTPException(status_code=404, detail="No cart found for the user")

    # Step 2: Fetch all cart products with related product and size details
    cart_products = session.exec(
        select(CartProduct)       
        .where(CartProduct.cart_id == cart.cart_id)
    ).all()

    # # Step 3: Format the response
    # products_list = []
    # for cart_product in cart_products:
    #     product_info = {
    #         "product_id": product.product_id,
    #         "product_name": product.product_name,
    #         "quantity": cart_product.quantity,         
    #     }
    #     products_list.append(product_info)

    # Step 4: Prepare the complete response
    response = {
        "message": "Cart fetched successfully",
        "user_id": cart.user_id,
        "cart_id": cart.cart_id,
        "products": cart_products,
        "delivery_address": cart.delivery_address,
        "nearest_branch": cart.nearest_branch,
        "products_total": cart.products_total,
        "delivery_charges": cart.delivery_charges,
        "discount": cart.discount,
        "sub_total": cart.sub_total,
    }

    return response



# ============================== DELETE ITEM FROM CART ================================
def remove_item_from_cart(cart_id: int, product_id: int, session: DB_SESSION):
    # Step 1: Fetch the CartProduct
    cart_product = session.exec(
        select(CartProduct).where(
            CartProduct.cart_id == cart_id,
            CartProduct.product_id == product_id,         
        )
    ).first()

    cart = session.exec(
        select(Cart).where(Cart.cart_id == cart_id)
    ).first()

    # Step 2: If the item doesn't exist, raise an error
    if not cart_product:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # Step 3: Remove the item from the cart
    session.delete(cart_product)
    session.commit()
    
    update_cart_totals(cart, session)

    return {"message": "Item removed from cart successfully"}



# ============================== UPDATE CART DETAILS LIKE DELIVERY ADDRESS, NEAREST BRANCH ETC ================================
def update_cart(cart_id: int, update_data: UpdateCart, session: DB_SESSION):
    """
    Updates the cart information based on the provided update data.
    Args:
        cart_id (int): The ID of the cart to update.
        update_data (UpdateCart): Data containing the fields to update in the cart.
        session (Session): Database session for executing queries.
    Returns:
        str: Confirmation message indicating the cart was updated.
    """
    # Step 1: Fetch the cart
    cart = session.exec(select(Cart).where(Cart.cart_id == cart_id)).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    # Step 2: Update fields based on provided data
    # if update_data.delivery_address is not None:
        # Validate if the provided delivery_address exists in UserAddress table
        # address = session.exec(select(UserAddress).where(UserAddress.address_id == update_data.delivery_address)).first()
        # if not address:
        #     raise HTTPException(status_code=400, detail="Invalid delivery address ID")
    cart.delivery_address = update_data.delivery_address

    if update_data.nearest_branch is not None:
        cart.nearest_branch = update_data.nearest_branch

    if update_data.discount is not None:
        cart.discount = update_data.discount

    if update_data.delivery_charges is not None:
        cart.delivery_charges = update_data.delivery_charges

    # Update other fields
    cart.updated_at = datetime.now(timezone.utc)
    cart.sub_total = cart.products_total + cart.delivery_charges - cart.discount

    # Step 3: Commit changes to the database
    session.add(cart)
    session.commit()

    return {"message" : "Cart updated successfully"}