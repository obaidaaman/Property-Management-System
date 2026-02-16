import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()


def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> bool:
    """
    Sends an HTML email using SMTP.
    Returns True if successful, False otherwise.
    """

    server = None
    EMAIL_ADDRESS = os.getenv("SENDER_EMAIL")
    EMAIL_PASSWORD= os.getenv("APP_PASSWORD")
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = EMAIL_ADDRESS
        message["To"] = to_email

        part = MIMEText(body, "plain")
        message.attach(part)

        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")

        server = smtplib.SMTP(smtp_server, smtp_port)
        # server.set_debuglevel(1)

        # server.esmtp_features['auth'] = 'LOGIN PLAIN'
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        server.sendmail(EMAIL_ADDRESS, to_email, message.as_string())

        print("Email sent successfully")
        return True

    except smtplib.SMTPAuthenticationError:
        print("SMTP authentication failed. Check username/password.")
    except smtplib.SMTPConnectError:
        print("Unable to connect to SMTP server.")
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if server:
            server.quit()

    return False


