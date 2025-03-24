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
from sat_image import Sat_Image
from infer import Infer_Pic

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
    
def generate_unique_id():
    """Generates a unique ID using uuid4."""
    return str(uuid.uuid4())

# Route to Home Page
@app.route("/")
def home():
    quotes = Quote.query.all()  # Fetch all quotes from the database
    return render_template("index.html", quotes=quotes)
    
# Route to Generate Quote
@app.route("/geocode", methods=["POST"])
def geocode():  
    
    address = request.form["address"]
    
    api_key = "AIzaSyBPl2BN22N1olCSEKphDwv822foR4PlYF4"
    
    # Retrieve Lat Lon with Geocoordinates
    lat, lon = Geocoding.get_lat_lon(address, api_key)
    print(f"Latitude: {lat}, Longitude: {lon}")
    
    # Get the Sat view since we have the Lat & Lon
    map_filename = Sat_Image.download_google_maps_satellite(lat, lon)
    
    # Infer on the Sat View we got
    Infer_Pic.infer_krzak(map_filename) 
    
    return "This is a valid response"  # Return a string
    
# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
    
'''
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
    api_key = "AIzaSyBPl2BN22N1olCSEKphDwv822foR4PlYF4"  
    lat, lon = Geocoding.get_lat_lon(address, api_key)
    print(f"Latitude: {lat}, Longitude: {lon}")
    
    map_filename = Sat_Image.download_google_maps_satellite(lat, lon)
    Infer_Pic.infer_krzak(map_filename) 
    
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
'''
