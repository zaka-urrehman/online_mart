from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select
from fastapi import HTTPException

from app.db.db_connection import DB_SESSION
from app.models.models import Product, AddProduct, ProductSize, Size, Category

from sqlalchemy.orm import joinedload

# ========================================= GET ALL PRODUCTS =====================================================

def get_all_products(session: DB_SESSION):
    """
    Retrieve all products from the database.
    """
    try:
        # print("Step 1: Fetching products from the database")
        statement = select(Product)
        products = session.exec(statement).all()
        # print("Step 2: Products fetched successfully:", products)

        product_list = []
        # n = 1
        for product in products:
            # print(f"Step 3 loop{n}: Processing product with ID: {product.product_id}")

            # Fetch associated sizes
            statement = select(Size).join(ProductSize).where(ProductSize.product_id == product.product_id)
            sizes = session.exec(statement).all()
            # print(f"Step 4 loop{n}: Sizes fetched for product ID {product.product_id}: {sizes}")

            # Convert sizes to dictionaries for the response
            sizes_list = [size.model_dump() for size in sizes]
            # print(f"Step 5 loop{n}: Sizes list created for product ID {product.product_id}: {sizes_list}")

            # Convert product to a dictionary for the response
            product_dict = product.model_dump()  # Convert product to dictionary
            # print(f"Step 6 loop{n}: Product dictionary before adding sizes for product ID {product.product_id}: {product_dict}")

            # Add the sizes field to the dictionary (not as part of the SQLAlchemy object)
            product_dict['sizes'] = sizes_list
            # print(f"Step 7 loop{n}: Final product dictionary for product ID {product.product_id}: {product_dict}")

            product_list.append(product_dict)
            # n+=1
        # print("Step 8: Final list of all products:", product_list)
        return product_list

    except Exception as e:
        # print("Error occurred:", str(e))
        raise HTTPException(status_code=500, detail="An error occurred while fetching products.")


# ========================================= GET PRODUCT BY ID ====================================================

def get_product_by_id(product_id: int, session: DB_SESSION):
    """
    Retrieve a product by its ID along with its associated sizes.
    """
    statement = select(Product).options(joinedload(Product.sizes).joinedload(ProductSize.size)).where(Product.product_id == product_id)
    product = session.exec(statement).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Add sizes to the product
    sizes = [{"size_id": product_size.size.size_id, "size_name": product_size.size.size_name}
             for product_size in product.sizes]

    product_dict = product.dict()  # Convert product to dict to append sizes
    product_dict["sizes"] = sizes

    return product_dict


# ========================================= CHECK IF CATEGORY EXISTS ===================================================

# Dependency to check if category exists
def validate_category_exists(cat_id: int, session: DB_SESSION):
    print("=== === === === === == ==")
    statement = select(Category).where(Category.cat_id == cat_id)
    category = session.exec(statement).first()

    if not category:
        raise HTTPException(
            status_code=400,
            detail=f"Category with ID {cat_id} does not exist."
        )
    return category

# ========================================= CREATE NEW PRODUCT ===================================================
async def add_product_in_db(new_product: AddProduct, session: DB_SESSION):
    # Validate category ID
    validate_category_exists(new_product.cat_id, session)
    

    statement = select(Product).where(Product.product_name == new_product.product_name)
    existing_product = session.exec(statement).first()

    # Check if a product with the same name already exists
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this name already exists.")

    # Create new product and commit to the database
    product = Product(**new_product.dict())
    session.add(product)
    session.commit()
    session.refresh(product)

    return {
        "product_id": product.product_id,
        "product_name": product.product_name,
    }


# ========================================= UPDATE PRODUCT =======================================================

def update_product_in_db(product_id: int, updated_product: AddProduct, session: DB_SESSION):
    """
    Update an existing product in the database.
    """
    validate_category_exists(updated_product.cat_id, session)
    # Fetch the product to update
    product = session.exec(select(Product).where(Product.product_id == product_id)).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in updated_product.dict(exclude_unset=True).items():
        setattr(product, key, value)

    session.commit()
    session.refresh(product)

    return product

# ========================================= DELETE PRODUCT =======================================================

def delete_product_from_db(product_id: int, session: DB_SESSION):
    """
    Delete a product from the database.
    """
    product = session.exec(select(Product).where(Product.product_id == product_id)).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    session.delete(product)
    session.commit()

    return {"message": f"Product with ID {product_id} deleted successfully."}

# ========================================= ASSIGN SIZES TO PRODUCT ==============================================

def assign_sizes_to_product(product_id: int, size_ids: list[int], session: DB_SESSION):
    """
    Assign new sizes to a product without removing the existing ones.
    """
    product = session.exec(select(Product).where(Product.product_id == product_id)).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get current sizes assigned to the product
    existing_sizes = session.exec(
        select(ProductSize.size_id).where(ProductSize.product_id == product_id)
    ).all()

    existing_size_ids = {size_id for (size_id,) in existing_sizes}

    # Add only the sizes that are not already assigned
    for size_id in size_ids:
        if size_id not in existing_size_ids:
            product_size = ProductSize(product_id=product_id, size_id=size_id)
            session.add(product_size)

    session.commit()

    return {"message": "Sizes assigned to product successfully."}

