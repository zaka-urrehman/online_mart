import smtplib

from sqlmodel import Session
from datetime import datetime

from app.db.db_connection import engine 
from app.models.email_model import NotificationBase
from app.settings import GOOGLE_APP_PASSWORD, NOTIFICATION_SENDER_EMAIL
from app.models.email_model import NotificationBase, Notification, NotificationTypeEnum

# =================================================================================================
def send_email_notification(notification_data: NotificationBase):
    # SMTP server details
    smtp_server = "smtp.gmail.com"  # Example for Gmail
    smtp_port = 587  # Port for TLS
    sender_email = NOTIFICATION_SENDER_EMAIL  # Replace with your email
    sender_password =  GOOGLE_APP_PASSWORD # Replace with your email password
    receiver_email = notification_data.email

    # Email content
    subject = notification_data.title
    body = notification_data.message
    message = f"Subject: {subject}\n\n{body}"

    try:
        # Create a secure connection to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection

        # Login to the email account
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, receiver_email, message)

        # Close the connection
        server.quit()

        add_notification_to_db(
            notification_data=notification_data,
            notification_type=NotificationTypeEnum.REGISTER_ALERT, # TODO:  CHECK TYPE OF NOTIFICATION FIRST AND THEN INSERT IT INTO DB OR DIRECTLY INSERT THE "notification_data.event_type" to make it dynamic
            status="sent"
        )

        return {"message": "Notification sent successfully"}

    except Exception as e:
        add_notification_to_db(
            notification_data=notification_data,
            notification_type=NotificationTypeEnum.REGISTER_ALERT,  # TODO:  CHECK TYPE OF NOTIFICATION FIRST AND THEN INSERT IT INTO DB OR DIRECTLY INSERT THE "notification_data.event_type" to make it dynamic
            status="not sent"
        )
        return {"error": f"Failed to send email: {str(e)}"}
    

# =================================================================================================


def add_notification_to_db(
    notification_data: NotificationBase, 
    notification_type: NotificationTypeEnum,
    status: str = "sent"
):
    """
    Adds a notification record to the database using a session created with the 'with' block.

    Args:
        notification_data (NotificationBase): The notification data to be saved.
        notification_type (NotificationTypeEnum): The type of the notification.
        status (str): Status of the notification (default is 'sent').
    """
    try:
        # Create a session using the 'with' block
        with Session(engine) as session:
            # Create a new Notification instance
            new_notification = Notification(
                email=notification_data.email,
                title=notification_data.title,
                message=notification_data.message,
                notification_type=notification_type,
                status=status,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Add the notification to the database session
            session.add(new_notification)
            session.commit()
            session.refresh(new_notification)  # Refresh to get the newly created ID

            print(f"Notification added to DB: {new_notification}")
            return new_notification

    except Exception as e:
        print(f"Failed to add notification to DB: {e}")
        raise
