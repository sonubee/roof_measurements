from flask import Flask, render_template, request, send_file
import openai
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os
import ee
import geemap
import json
import uuid
import sys
import logging
import requests
import cv2
import numpy as np
import torch
from ultralytics import YOLO
import matplotlib.pyplot as plt

service_account = 'first-key@ee-notifications3972.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'ee-notifications3972-a04ee465a57f.json')
ee.Initialize(credentials)

print("INITIALIZED$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$2")

# Configure OpenAI API Key
openai.api_key = "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"

app = Flask(__name__)

# Set a secret key (Make sure this is unique and secret)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your-very-secret-key")  # Use an environment variable or fallback

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
    roof_square_feet = db.Column(db.Float, nullable=True)  # Roof Area
    roof_image_url = db.Column(db.String(255), nullable=True)  # Store Image URL

# Initialize Database
with app.app_context():
    db.create_all()
    
# Initialize Flask-Admin
admin = Admin(app, name="Quote Admin", template_mode="bootstrap3")
admin.add_view(ModelView(Quote, db.session))

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
    
def save_raw_image_to_drive(lat, lon, filename="raw_satellite_image"):
    """
    Saves the raw, unmodified Sentinel-2 satellite image directly to Google Drive.
    
    Args:
        lat (float): Latitude of the house.
        lon (float): Longitude of the house.
        filename (str): Name of the output image file (without extension).
    
    Returns:
        str: Google Drive file name.
    """
    filename = generate_unique_id()
    print(lat, " + ", lon)

    # Define the point for the house location
    point = ee.Geometry.Point(lon, lat)

    # Use NAIP imagery (USA only, 1m resolution)
    collection = ee.ImageCollection("USDA/NAIP/DOQQ") \
        .filterBounds(point) \
        .filterDate("2022-01-01", "2024-12-31") \
        .sort("system:time_start", False)  # Get latest image

    latest_image = collection.first()

    # Select RGB bands (NAIP bands are ["R", "G", "B", "N"])
    roof_image = latest_image.select(["R", "G", "B"])

    # Define export region (increase buffer for larger area)
    region = point.buffer(15).bounds()  # Adjust based on house size

    # Export image to Google Drive
    task = ee.batch.Export.image.toDrive(
        image=roof_image.toUint16(),
        description=filename,
        folder="EarthEngineExports",
        fileNamePrefix=filename,
        scale=1,  # 1m resolution
        region=region,
        fileFormat="GEO_TIFF"
    )


    # Start the export task
    task.start()
    
    print("Export started: Image will be available in Google Drive folder 'EarthEngineExports' as ", filename, ".tif")

    return f"Export started: Image will be available in Google Drive folder 'EarthEngineExports' as {filename}.tif"
    
def download_google_maps_satellite(lat, lon):
    """
    Downloads a high-resolution satellite image from Google Static Maps API.
    """
    API_KEY = "AIzaSyBPl2BN22N1olCSEKphDwv822foR4PlYF4"  # Replace with your API key
    ZOOM = 20  # Max zoom for high detail (adjust if needed)
    SIZE = "640x640"  # Max image size (you can stitch multiple images for ultra-high res)
    MAP_TYPE = "satellite"
    
    filename = generate_unique_id()
    filename = filename + ".png"
    print(lat, " + ", lon)

    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={ZOOM}&size={SIZE}&maptype={MAP_TYPE}&key={API_KEY}"

    response = requests.get(url)

    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"High-resolution image saved as {filename}")
    else:
        print("Error downloading image:", response.status_code)
        
# Function to detect roofs using YOLOv8
def detect_roofs(image_path, output_path="roof_detected.png"):
    # Load YOLOv8 pre-trained model (best for object detection)
    model = YOLO("yolov8n.pt")  # Use "yolov8m.pt" for better accuracy

    # Load image
    image = cv2.imread(image_path)

    # Run inference
    results = model(image)

    # Draw detections on image
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0]
            label = f"Roof ({conf:.2f})"
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Save & show image with detections
    cv2.imwrite(output_path, image)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.show()
    print(f"Roof detection saved as {output_path}")

def generate_unique_id():
    """Generates a unique ID using uuid4."""
    return str(uuid.uuid4())

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
    
    lat, lon = 37.402572004102694, -121.8223697685583
    #lat, lon = 37.7749, -122.4194  # Example: San Francisco
    print("Roof Coming Below*********************************************************************")
    
    # Example Usage

    result = save_raw_image_to_drive(lat, lon)
    print(result)
    
    print("here14")
    
    detect_roofs("1ff95725-5cbb-436d-a934-e035fdce4ee9.png")
    
    return "This is a valid response"  # Return a string
    
# Route to View & Download Images
@app.route("/images")
def list_images():
    quotes = Quote.query.all()
    return render_template("images.html", quotes=quotes)

@app.route("/download/<filename>")
def download_image(filename):
    """Download an image from the static/images directory."""
    file_path = os.path.join("static/images", filename)
    return send_file(file_path, as_attachment=True)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
