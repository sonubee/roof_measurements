from flask import Flask, render_template, request
import openai
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import ee
import geemap

# Initialize Earth Engine
ee.Initialize()

app = Flask(__name__)

# Check if running on Heroku (PostgreSQL) or locally (SQLite)
if "DATABASE_URL" in os.environ:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"].replace("postgres://", "postgresql://", 1)  # Heroku fix
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quotes.db"  # Local SQLite

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

# Define Database Model
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    recipient_email = db.Column(db.String(100), nullable=False)
    product_details = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    validity = db.Column(db.Integer, nullable=False)
    pdf_filename = db.Column(db.String(100), nullable=False)

# Initialize Database
with app.app_context():
    db.create_all()

# Configure OpenAI API Key
openai.api_key = "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"

# Function to generate AI-powered email
def generate_quote_email(customer_name, product_details, price, validity):
    prompt = f"""
    Generate a professional email to {customer_name} for a quote.
    - Product/Service: {product_details}
    - Price: ${price}
    - Quote Validity: {validity} days
    The email should be polite, professional, and include a call to action.
    """
    
    response = openai.chat.completions.create(
        model="gpt-4-turbo",  # Use "gpt-4-turbo" for cost-effective performance
        messages=[{"role": "system", "content": "You are a helpful assistant that writes professional emails."},
                  {"role": "user", "content": prompt}]
    )
    print("here")
    response_message = response.choices[0].message.content
    print(response_message )
    print("here2")
    
    if hasattr(response.choices[0].message, "content"):
           print(response.choices[0].message)
    
    return response_message 

'''
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes professional emails."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response["choices"][0]["message"]["content"]
'''
# Function to generate PDF quote
def generate_pdf_quote(customer_name, product_details, price, validity):
    filename = f"quote_{customer_name.replace(' ', '_')}.pdf"
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
        
# Function to calculate roof area
def calculate_roof_area(lat, lon):
    # Define the point for the house location
    point = ee.Geometry.Point(lon, lat)

    # Use high-resolution satellite imagery
    image = ee.Image('COPERNICUS/S2_SR').select('B4')  # Red band for better visualization

    # Thresholding to detect roof
    roof_mask = image.gt(1000)  # Adjust threshold based on region
    roof_area = roof_mask.multiply(ee.Image.pixelArea())

    # Reduce region to get total area
    stats = roof_area.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=point.buffer(20),  # Adjust based on house size
        scale=10,
        maxPixels=1e9
    )

    area_m2 = stats.getInfo().get('B4', 0)  # Get roof area in square meters
    area_ft2 = area_m2 * 10.764  # Convert to square feet
    return round(area_ft2, 2)

# Route to Home Page
@app.route("/")
def home():
    quotes = Quote.query.all()  # Fetch all quotes from the database
    return render_template("index.html", quotes=quotes)

# Route to Generate Quote
@app.route("/generate", methods=["POST"])
def generate():
    customer_name = request.form["customer_name"]
    recipient_email = request.form["recipient_email"]
    product_details = request.form["product_details"]
    price = float(request.form["price"])
    validity = int(request.form["validity"])

    # Generate AI-powered email
    email_content = generate_quote_email(customer_name, product_details, price, validity)

    # Generate PDF
    pdf_filename = generate_pdf_quote(customer_name, product_details, price, validity)

    # Store Quote in Database
    new_quote = Quote(
        customer_name=customer_name,
        recipient_email=recipient_email,
        product_details=product_details,
        price=price,
        validity=validity,
        pdf_filename=pdf_filename
    )
    db.session.add(new_quote)
    db.session.commit()

    # Send Email with PDF
    send_email_with_pdf(recipient_email, "Your Quote", email_content, pdf_filename)
    
    lat, lon = 37.7749, -122.4194
    print("Roof Coming Below*********************************************************************")
    print(calculate_roof_area(lat, lon))

    return f"Quote sent successfully to {recipient_email}!"

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
