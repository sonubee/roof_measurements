from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os
import ee
import geemap
import json
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
from send_email import Email
from sat_image import Sat_Image
from infer import Infer_Pic
from solarAPI import SolarAPI
import googlemaps
import tkinter as tk
from extract_home import Extract_Now
from property_report import Property_Report
from get_keys import Get_Keys
from homesage import HomeSage

api_key = Get_Keys.get_gcloud_key()

print("INITIALIZED")

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
    roof_square_feet = db.Column(db.Float, nullable=True)  # Roof Area
    roof_image_url = db.Column(db.String(255), nullable=True)  # Store Image URL

# Initialize Database
with app.app_context():
    db.create_all()
    
# Initialize Flask-Admin
admin = Admin(app, name="Quote Admin", template_mode="bootstrap3")
admin.add_view(ModelView(Quote, db.session))

# Route to Home Page
@app.route("/")
def home():
    
    quotes = Quote.query.all()  # Fetch all quotes from the database
    return render_template("index.html", quotes=quotes)
    
# Route to Generate Quote
@app.route("/geocode", methods=["POST"])
def geocode():  
    
    address = request.form["address"]
    
    # Retrieve Lat Lon with Geocoordinates
    lat, lon = Geocoding.get_lat_lon(address, api_key)
    print(f"Latitude: {lat}, Longitude: {lon}")
    
    roof_measurement = SolarAPI.get_roof_dim(lat, lon, api_key)
    
    # Get the Sat view since we have the Lat & Lon
    map_filename = Sat_Image.download_google_maps_satellite(lat, lon, address, api_key)
    
    # Infer on the Sat View we got
    Infer_Pic.infer_krzak(map_filename) 
    
    Extract_Now.start_work(map_filename, lat, lon)
    
    roofType = HomeSage.return_roof(address)
    print(roofType)
    
    Property_Report.gen_report(address, roof_measurement, lat, lon, map_filename, "annotated_polygon.jpg", "cropped_buffer.png", roofType)
    
    data = {
        "address": address,
        "House Age": 30,
        "Roof": roofType
    }
    
    print(data)
    
    return "This is a valid response"  # Return a string
    
# Run the Flask app

if __name__ == "__main__":
    app.run(debug=True)