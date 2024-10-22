from fastapi.testclient import TestClient
from app.main import app
# from app.settings import TESTING_PRODUCT_ID, TESTING_SIZE_ID, TESTING_CATEGORY_ID

client = TestClient(app)

# testing_product_id = TESTING_PRODUCT_ID
# testing_category_id = TESTING_CATEGORY_ID
# testing_size_id = TESTING_SIZE_ID

# print("ids here: " , testing_category_id, testing_product_id, testing_size_id)

# ========================================= ADD NEW CATEGORY =========================================
def test_add_category():
    new_category = {
        # "cat_id": 100,
        "cat_name": "Testing Category",
        "description": "This is a Testing category"
    }
    response = client.post("/category/add-category", json=new_category)
    assert response.status_code == 200
    assert response.json()["message"] == "Category added successfully"

# ========================================= UPDATE CATEGORY =========================================
# def test_update_category():
#     updated_category = {
#         "name": "Updated Category",
#         "description": "Test Category Updated"
#     }
#     response = client.put(f"/category/update-category/{testing_category_id}", json=updated_category)
#     assert response.status_code == 200
#     assert response.json()["message"] == "Category updated successfully"


# # ========================================= GET ALL CATEGORIES =========================================
def test_get_categories():
    response = client.get("/category/categories")
    assert response.status_code == 200
    assert response.json()["message"] == "Categories fetched successfully"


# # ========================================= GET CATEGORY BY ID =========================================
# def test_get_category():
#     response = client.get(f"/category/{testing_category_id}")
#     assert response.status_code == 200
#     assert "category" in response.json()



# # ========================================= ADD NEW SIZE =========================================
def test_add_size():
    new_size = {
        # "size_id": testing_size_id,
        "size_name": "Testing Size"
    }
    response = client.post("/size/add-size", json=new_size)
    assert response.status_code == 200
    assert response.json()["size_name"] == "Testing Size"

# # ========================================= UPDATE SIZE =========================================
# def test_update_size():
#     updated_size = {
#         "size_id": testing_size_id,
#         "size_name": "Updated Testing Size"
#     }
#     response = client.put("/size/update-size/1", json=updated_size)
#     assert response.status_code == 200
#     assert response.json()["size_name"] == "Updated Testing Size"

# # ========================================= GET SIZES =========================================
def test_get_sizes():
    response = client.get("/size/sizes")
    assert response.status_code == 200
    assert len(response.json()) >= 1

# # ========================================= GET SIZE BY ID =========================================
# def test_get_size():
#     response = client.get(f"/size/{testing_size_id}")
#     assert response.status_code == 200
#     assert "size" in response.json()

# # ========================================= ADD NEW PRODUCT =========================================
def test_add_product():
    new_product = {
    # "product_id": testing_product_id,
    "product_name": "Testing Product",
    "description": "not available",
    "brand": "string",
    "expiry": "2024-10-15T18:24:42.278Z",
    "price": 10,
    "quantity": 10,
    "cat_id": 4
    }
    response = client.post("/product/add-product", json=new_product)
    assert response.status_code == 200
    assert response.json()["message"] == "Product added successfully"

# # ========================================= UPDATE PRODUCT =========================================
# def test_update_product():
#     updated_product = {
#     "product_name": "updated testing product",
#     "description": "testing product has successfully been updated",
#     "brand": "string",
#     "expiry": "2024-10-15T18:25:35.954Z",
#     "price": 20,
#     "quantity": 0,
#     "cat_id": 4
#     }
#     response = client.put(f"/product/update-product/{testing_product_id}", json=updated_product)
#     assert response.status_code == 200
#     assert response.json()["message"] == "product updated successfully"


# # ========================================= GET ALL PRODUCTS =========================================
def test_get_products():
    response = client.get("/product/products")
    assert response.status_code == 200
    assert len(response.json()) >= 1

# # ========================================= GET PRODUCT BY ID =========================================
# def test_get_product():
#     response = client.get(f"/product/{testing_product_id}")
#     assert response.status_code == 200
#     assert "product" in response.json()


# # ========================================= ASSIGN SIZES TO PRODUCT  =========================================
# def test_assign_sizes_to_product():
#     size_ids = [testing_size_id]
#     response = client.post(f"/product/assign-sizes/{testing_product_id}", json=size_ids)
#     assert response.status_code == 200 
#     assert response.json()["message"] == "Sizes assigned to product successfully."

# #========================================  DELETE PRODUCT ========================================= 
# def test_delete_product():
#     response = client.delete(f"/product/delete-product/{testing_product_id}")
#     assert response.status_code == 200
#     assert response.json()["message"] == f"Product with ID {testing_product_id} deleted successfully"

# # =========================================  DELETE SIZE =========================================

# def test_delete_size():
#     response = client.delete(f"/size/delete-size/{testing_size_id}")
#     assert response.status_code == 200
#     assert response.json()["message"] == "Size deleted successfully"

# # ========================================= DELETE CATEGORY =========================================
# def test_delete_category():
#     response = client.delete(f"/category/delete-category/{testing_category_id}")
#     assert response.status_code == 200
#     assert response.json()["message"] == "Category deleted successfully"