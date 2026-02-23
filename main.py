import smtplib
import os
from email.message import EmailMessage

def send_test_email():
    # 1. Setup the message
    msg = EmailMessage()
    msg['Subject'] = "Aero-Bot Pulse Check"
    msg['From'] = "sfeinberg@gmail.com" # Replace with your email
    msg['To'] = "sfeinberg@gmail.com"   # Send it to yourself
    msg.set_content("The connection is live. If you are reading this, your GitHub Secrets and App Password are set up correctly.")

    # 2. Extract Secrets
    email_user = "sfeinberg@gmail.com" # Replace with your email
    email_pass = os.environ.get("EMAIL_PASSWORD")

    print(f"Attempting login for: {email_user}")

    # 3. Connect and Send
    try:
        # We use port 465 for SMTP_SSL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_user, email_pass)
            print("Login successful!")
            smtp.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print(f"FAILED to send email. Error: {e}")

if __name__ == "__main__":
    send_test_email()
