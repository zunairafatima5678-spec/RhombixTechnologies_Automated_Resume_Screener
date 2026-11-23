import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_shortlist_email(receiver_email, candidate_name, sender_email, sender_password):
    if not sender_email or not sender_password or not receiver_email or receiver_email == "Not Found":
        return False

    smtp_server = "smtp.gmail.com"
    clean_name = candidate_name.strip() if candidate_name and candidate_name.strip() else "Candidate"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Congratulations! You Are Selected - Rhombix Technologies"
    message["From"] = f"Rhombix Technologies <{sender_email}>"
    message["To"] = receiver_email

    text = (
        f"Dear {clean_name},\n\n"
        "Congratulations! You have been selected to move forward in the hiring process "
        "at Rhombix Technologies.\n\n"
        "Our team will contact you again regarding your interview schedule.\n\n"
        "Best regards,\n"
        "HR Team\n"
        "Rhombix Technologies"
    )

    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1f2937; line-height: 1.6; background-color: #f9fafb; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 24px;">
          <h2 style="color: #1d4ed8; margin-top: 0;">Congratulations, {clean_name}!</h2>
          <p>We are pleased to inform you that you have been <strong>selected</strong> to move forward in the hiring process at <strong>Rhombix Technologies</strong>.</p>
          <p>You will be contacted again with details regarding your interview.</p>
          <br>
          <p style="margin: 0;">Best regards,</p>
          <p style="margin: 4px 0 0 0;"><strong>HR Team</strong><br>Rhombix Technologies</p>
        </div>
      </body>
    </html>
    """

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(smtp_server, 587, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e_587:
        print(f"Port 587 failed for {receiver_email}: {e_587}")

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, 465, context=context, timeout=30) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e_465:
        print(f"Error sending email to {receiver_email}: {e_465}")
        return False