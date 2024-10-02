from sqlmodel import Session, select
from typing import Annotated
from fastapi import Depends, HTTPException
from app.models.user_models import UserRegister, User
from app.db.db_connection import DB_SESSION
from app.utils.auth import hash_password

#-----------------------------------------------------------------------------------------------------------------------

async def add_admin_in_db(admin_details: UserRegister, session: DB_SESSION):
    # Step-1: Check if admin already exists (based on email or phone)
    statement = select(User).where(
        (User.email == admin_details.email) | (User.phone == admin_details.phone),
        User.role == "admin"
    )
    existing_admin = session.exec(statement).first()

    # Step-2: Raise an error if admin already exists
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin with this email or phone already exists.")

    # Step-3: Hash the password before storing it
    hashed_password = hash_password(admin_details.password)
    admin_details.password = hashed_password

    # Step-4: Create a new admin (ensure role is "admin")
    new_admin = User(**admin_details.model_dump(), role="admin")

    # Add and commit to the database
    session.add(new_admin)
    session.commit()
    session.refresh(new_admin)

    return new_admin

#-----------------------------------------------------------------------------------------------------------------------

async def get_all_admins(session: DB_SESSION):
    try:
        # Step-1: Fetch all admins from the database (filter by role="admin")
        statement = select(User).where(User.role == "admin")
        admins = session.exec(statement).all()
        return admins

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

#-----------------------------------------------------------------------------------------------------------------------

async def update_admin_in_db(admin_id: int, admin_details: User, session: DB_SESSION):
    try:
        # Step-1: Check if admin exists
        admin_to_update = session.get(User, admin_id)
        if not admin_to_update or admin_to_update.role != "admin":
            raise HTTPException(status_code=400, detail="Admin not found or not an admin.")

        # Step-2: Hash the password if a new password is provided
        if admin_details.password:
            hashed_password = hash_password(admin_details.password)
            admin_to_update.password = hashed_password

        # Step-3: Update the admin's fields
        admin_to_update.first_name = admin_details.first_name
        admin_to_update.last_name = admin_details.last_name
        admin_to_update.email = admin_details.email
        admin_to_update.phone = admin_details.phone

        # Step-4: Commit the changes
        session.commit()
        session.refresh(admin_to_update)

        return admin_to_update

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"An unexpected error occurred while updating the admin: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

#-----------------------------------------------------------------------------------------------------------------------

async def delete_admin_from_db(admin_id: int, session: DB_SESSION):
    try:
        # Step-1: Fetch the admin by ID
        admin_to_delete = session.get(User, admin_id)

        # Step-2: If admin does not exist or is not an admin, raise an error
        if not admin_to_delete or admin_to_delete.role != "admin":
            raise HTTPException(status_code=404, detail="Admin not found or not an admin.")

        # Step-3: Delete the admin
        session.delete(admin_to_delete)
        session.commit()

        return {"message": f"Admin with id {admin_id} deleted successfully"}

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"An unexpected error occurred while deleting the admin: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
