from flask import Flask, render_template, request, send_file
import openai
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
from PIL import Image
from roboflow import Roboflow
from get_coord import Geocoding
from aiemail import Open
from gen_pdf import GenPDF
from send_email import Email

service_account = 'first-key@ee-notifications3972.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'ee-notifications3972-a04ee465a57f.json')
ee.Initialize(credentials)

print("INITIALIZED")

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
    
def save_raw_image_to_drive(lat, lon):
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
        
    return filename
    
def infer_krzak(filename3):
    # define the image url to use for inference
    
    #image = cv2.imread(filename)
    
    print("here14.1")
    
    api_key="WC65G8Eh1ol0B7Aub5oW"
    rf = Roboflow(api_key="WC65G8Eh1ol0B7Aub5oW")
    print("here14.2")
   
    url = f"https://api.roboflow.com/?api_key={api_key}"
    
    print("here14.3")

    response = requests.get(url)
    
    print("here14.4")

    if response.status_code == 200:
        workspace_info = response.json()
        print("Active workspace info:")
        print(workspace_info)
    else:
        print("Error:", response.status_code, response.text)
        
    print("here14.5")
   
    project = rf.workspace().project("my-first-project-bt5zl")
    
    print("here14.6")
    
    model = project.version(1).model
    
    print("here14.7")
    
    workspace = rf.workspace()
    print("Workspace:", workspace)

    # Replace 'your-project-name' with the exact project name from your dashboard.
    project = workspace.project("krzak")
    print("Project:", project)
    
    # Load your image
    img = Image.open(filename3)

    # Check the mode and convert to RGB if needed
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Save as JPEG
    
    if filename3.lower().endswith(".png"):
        new_filename = os.path.splitext(filename3)[0] + ".jpg"
        os.rename(filename3, new_filename)
        print(f"Renamed '{filename3}' to '{new_filename}'")
    else:
        print(f"'{filename3}' is not a PNG file.")
    
    img.save(filename3, "JPEG")

    # Check if the version exists
    try:
        model = project.version(1).model
        print("Model loaded successfully:", model)
    except Exception as e:
        print("Error loading model:", e)
        
    # Local or URL image
    prediction = model.predict(filename3).json()
    
    with open('pred_returned.json', 'r') as file:
        # The 'with' statement ensures the file is automatically closed
        # even if errors occur.
        data = json.load(file)
    
    print(prediction)
 
    print("here14.8")
    
    image_path = filename3  # Replace with your image file path
    image = cv2.imread(image_path)
    
    # Draw bounding boxes and labels on the image
    for pred in prediction.get("predictions", []):
        x = int(pred["x"])
        y = int(pred["y"])
        w = int(pred["width"])
        h = int(pred["height"])
        label = f"{pred['class']} {pred['confidence']:.2f}"
        
        # Draw rectangle (bounding box)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # Draw label above the rectangle
        cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)
 
    # Save the annotated image
    annotated_image_path = "annotated_output.jpg"
    cv2.imwrite(annotated_image_path, image)
    print(f"Annotated image saved as {annotated_image_path}")
   

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
    email_content = Open.generate_quote_email(customer_name, product_details, price, validity)
    
    print("email generated")

    # Generate PDF
    pdf_filename = GenPDF.generate_pdf_quote(customer_name, product_details, price, validity)

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
        
    #Send Email with PDf    
    Email.send_email_with_pdf(recipient_email, "Your Quote", email_content, pdf_filename)
    
    # Example usage:
    address = "3972 Myinda Dr. San Jose, CA. 95132"
    api_key = "AIzaSyBPl2BN22N1olCSEKphDwv822foR4PlYF4"  # Replace with your actual API key
    #lat, lon = get_lat_lon(address, api_key)
    lat, lon = Geocoding.get_lat_lon(address, api_key)
    print(f"Latitude: {lat}, Longitude: {lon}")
    
    # Example Usage

    #result = save_raw_image_to_drive(lat, lon)
    #print(result)
    
    print("here14")
    
    filename2 = download_google_maps_satellite(lat, lon)
    print(filename2)
    
    infer_krzak(filename2)
    
    print("here15")    
    
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
