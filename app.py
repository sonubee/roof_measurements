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
        
def calculate_roof_area(lat, lon):
    """
    Calculates the approximate roof area in square feet for a given location.
    
    Args:
        lat (float): Latitude of the house.
        lon (float): Longitude of the house.
    
    Returns:
        float: Estimated roof area in square feet.
    """
    
    # Define the point for the house location
    point = ee.Geometry.Point(lon, lat)

    # Load the most recent Sentinel-2 image (Surface Reflectance)
    collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterBounds(point) \
        .filterDate("2024-01-01", "2024-12-31") \
        .sort("system:time_start", False)

    latest_image = collection.first()  # Get the most recent image

    # Select Red Band (B4) - Useful for rooftop detection
    red_band = latest_image.select("B4")

    # Apply a threshold to segment the roof (Adjust this value if necessary)
    roof_mask = red_band.gt(1000)  # Threshold might need fine-tuning based on location
    roof_area = roof_mask.multiply(ee.Image.pixelArea())  # Convert to area (m²)

    # Calculate the total roof area using reduceRegion
    stats = roof_area.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=point.buffer(20),  # Adjust buffer size based on roof area
        scale=10,  # Sentinel-2 resolution is 10m per pixel
        maxPixels=1e9
    )

    # Extract area in square meters
    area_m2 = stats.getInfo().get("B4", 0)  # Retrieve roof area (m²)

    # Convert square meters to square feet (1 m² = 10.764 ft²)
    area_ft2 = area_m2 * 10.764

    # Return the estimated roof area in square feet
    return round(area_ft2, 2)
'''
def download_roof_image(lat, lon, filename="roof_image.tif"):
    """
    Downloads a satellite image of the house with the detected roof area.
    
    Args:
        lat (float): Latitude of the house.
        lon (float): Longitude of the house.
        filename (str): Name of the output image file.
    
    Returns:
        str: File path of the downloaded image.
    """
    
    print("here11")

    # Define the point for the house location
    point = ee.Geometry.Point(lon, lat)

    # Load the most recent Sentinel-2 image
    collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterBounds(point) \
        .filterDate("2024-01-01", "2024-12-31") \
        .sort("system:time_start", False)

    latest_image = collection.first()

    # Select RGB Bands (True Color)
    true_color = latest_image.select(["B4", "B3", "B2"])  # Red, Green, Blue

    # Apply a threshold to detect the roof area
    roof_mask = latest_image.select("B4").gt(1000)  # Adjust threshold if necessary

    # Overlay detected roof area in red
    roof_overlay = true_color.visualize(min=0, max=3000) \
        .blend(roof_mask.visualize(palette=["FF0000"], opacity=0.5))  # Red roof area
        
    print("here11.5")

    # Define the export region (adjust buffer size)
    region = point.buffer(50).bounds()
    
    print("here11.51")

    # Download image using geemap
    output_file = f"./{filename}"
    geemap.ee_export_image(roof_overlay, filename=output_file, scale=10, region=region, file_per_band=False)

    return output_file
'''    
def save_roof_image_to_drive(lat, lon, filename="roof_measurement4"):
    """
    Saves the roof measurement image directly to Google Drive using a service account.
    
    Args:
        lat (float): Latitude of the house.
        lon (float): Longitude of the house.
        filename (str): Name of the output image file (without extension).
    
    Returns:
        str: Google Drive file URL.
    """
    
    filename = generate_unique_id()

    # Define the point for the house location
    point = ee.Geometry.Point(lon, lat)

    # Load the most recent Sentinel-2 image
    collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterBounds(point) \
        .filterDate("2024-01-01", "2024-12-31") \
        .sort("system:time_start", False)

    latest_image = collection.first()

    # Select RGB Bands (True Color)
    true_color = latest_image.select(["B4", "B3", "B2"])  # Red, Green, Blue

    # Apply a threshold to detect the roof area
    roof_mask = latest_image.select("B4").gt(1000)  # Adjust threshold if necessary

    # Overlay detected roof area in red
    roof_overlay = true_color.visualize(min=0, max=3000) \
        .blend(roof_mask.visualize(palette=["FF0000"], opacity=0.5))  # Red roof area

    # Define the export region (adjust buffer size)
    region = point.buffer(50).bounds()

    # Export image to Google Drive
    task = ee.batch.Export.image.toDrive(
        image=roof_overlay,
        description=filename,
        folder="EarthEngineExports",  # Folder in Google Drive
        fileNamePrefix=filename,
        scale=10,
        region=region,
        fileFormat="GEO_TIFF"
    )

    # Start the export task
    task.start()

    # Generate Google Drive public URL
    drive_url = f"https://drive.google.com/uc?id={filename}"

    # Store URL in database
    quote = Quote.query.filter_by(customer_name="Example Customer").first()
    if quote:
        quote.roof_image_url = drive_url
        db.session.commit()

    return f"Export started: Image will be available at {drive_url}"
    
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
    
    #lat, lon = 37.7749, -122.4194
    lat, lon = 37.402572004102694, -121.8223697685583
    print("Roof Coming Below*********************************************************************")
    
    print("here8")
    print(calculate_roof_area(lat, lon))
    
    print("here9")

    #return f"Quote sent successfully to {recipient_email}!"
    
    print("here10")
    
    #image_path = download_roof_image(lat, lon, filename="roof_measurement.tif")
    
    print("here12")

    #print(f"Roof measurement image saved at: {image_path}")
    
    print("here13")
    
    result = save_roof_image_to_drive(lat, lon)
    print(result)
    
    print("here14")
    
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
