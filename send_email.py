import smtplib
from email.message import EmailMessage

class Email:

    # Function to send email with PDF attachment
    def send_email_with_pdf(recipient_email, subject, body, pdf_filename):
        sender_email = "notifications3972@gmail.com"  # Replace with your email
        sender_password = "tbbi eeyg mbuv ciqn"  # Replace with an app-specific password

        msg = EmailMessage()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.set_content(body)

        with open(pdf_filename, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=pdf_filename)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)