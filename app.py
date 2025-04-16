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
from fpdf import FPDF
from flask import redirect, url_for, session

api_key = Get_Keys.get_gcloud_key()

print("INITIALIZED")

app = Flask(__name__)
app.secret_key = 'your_secret_key' # Required for session management

# Route to Home Page
@app.route("/")
def home():
    
    return render_template("index.html")
    
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
    session['report_name'] = map_filename
    # map_image = Sat_Image.return_google_maps_satellite_image(lat, lon, address, api_key)
    print("after getting 2nd google map API image and before printing again in main class. is it the same?")
    # print(map_image)
    
    # Infer on the Sat View we got
    Infer_Pic.infer_krzak(map_filename) 
    print("before infer_roof")
    # Infer_Pic.infer_roof(map_image)
    print("got infer")
    
    Extract_Now.start_work(map_filename, lat, lon)
    
    roofType = HomeSage.return_roof(address)
    print(roofType)
    
    pdf = Property_Report.gen_report(address, roof_measurement, lat, lon, map_filename, "annotated_polygon.jpg", "cropped_buffer.png", roofType)
    
    print("got pdf")
    
    return redirect(url_for('download_report'))
    
    #return "This is a valid response"  # Return a string
    
@app.route('/download-report')
def download_report():
    
    map_filename = session.get('report_name')
    print("map: ", map_filename)
    
    # Replace 'property_report.pdf' with the actual path to your generated PDF
    return send_file(map_filename, as_attachment=True, download_name = map_filename)
    
# Run the Flask app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)