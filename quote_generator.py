import openai
import smtplib
from email.message import EmailMessage
from fpdf import FPDF
import os

# Step 1: Collect Quote Information
def get_quote_details():
    customer_name = input("Enter customer name: ")
    recipient_email = input("Enter customer email: ")
    product_details = input("Enter product/service details: ")
    price = input("Enter price: ")
    validity = input("Enter quote validity (in days): ")

    return customer_name, recipient_email, product_details, price, validity

# Step 2: Generate Email Content using ChatGPT

def generate_quote_email(customer_name, product_details, price, validity):
    from openai import OpenAI
   
    client = OpenAI(
    api_key = "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",
    )
    print("here0")
    
    prompt = f"""
    Generate a professional email to {customer_name} for a quote.
    - Product/Service: {product_details}
    - Price: ${price}
    - Quote Validity: {validity} days
    The email should be polite, professional, and include a call to action.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",  # Use "gpt-4-turbo" for cost-effective performance
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}]
    )
    print("here")
    response_message = response.choices[0].message.content
    print(response_message )
    print("here2")
    
    if hasattr(response.choices[0].message, "content"):
           print(response.choices[0].message)
    
    return response_message
    #return response.choices[0].message["content"]

# Step 3: Generate PDF Quote
def generate_pdf_quote(customer_name, product_details, price, validity, filename="quote.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Quotation", ln=True, align="C")
    pdf.ln(10)
    
    pdf.cell(200, 10, txt=f"Customer: {customer_name}", ln=True)
    pdf.cell(200, 10, txt=f"Product/Service: {product_details}", ln=True)
    pdf.cell(200, 10, txt=f"Price: ${price}", ln=True)
    pdf.cell(200, 10, txt=f"Quote Validity: {validity} days", ln=True)
    
    pdf.output(filename)
    return filename

# Step 4: Send Email with PDF Quote
def send_email_with_pdf(recipient_email, subject, body, pdf_filename):
    sender_email = "notifications3972@gmail.com"  # Replace with your email
    sender_password = "tbbi eeyg mbuv ciqn"  # Replace with an app-specific password

    print("here3")

    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    print(recipient_email)
    print(subject)
    print(body)
    
    msg.set_content(body)
    
    print("here4")
    print(customer_name)

    with open(pdf_filename, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=pdf_filename)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

# Run the full process
if __name__ == "__main__":
    customer_name, recipient_email, product_details, price, validity = get_quote_details()
    
    email_content = generate_quote_email(customer_name, product_details, price, validity)
    
    print("here2.5")
    print(email_content)
    
    pdf_filename = generate_pdf_quote(customer_name, product_details, price, validity)
    
    send_email_with_pdf(recipient_email, "Your Quote", email_content, pdf_filename)
    
    print("Quote sent successfully!")
