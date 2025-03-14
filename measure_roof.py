import ee
import geemap
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize Earth Engine
ee.Initialize()

# Flask app & Database setup
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quotes.db"  # Use PostgreSQL in production
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Define Quote Model
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    recipient_email = db.Column(db.String(100), nullable=False)
    product_details = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    validity = db.Column(db.Integer, nullable=False)
    pdf_filename = db.Column(db.String(100), nullable=False)
    roof_square_feet = db.Column(db.Float, nullable=True)  # New field

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

# Function to update quote with roof area
def update_quote_with_roof(quote_id, lat, lon):
    quote = Quote.query.get(quote_id)
    if quote:
        print(roof_sq_ft = calculate_roof_area(lat, lon))
        '''
        quote.roof_square_feet = roof_sq_ft
        db.session.commit()
        return f"Updated Quote ID {quote_id} with Roof Area: {roof_sq_ft} sq ft"
    else:
        return "Quote not found."
        '''

# Run this script to update a quote
if __name__ == "__main__":
    quote_id = 1  # Change to the actual quote ID
    lat, lon = 37.7749, -122.4194  # Example: San Francisco
    result = update_quote_with_roof(quote_id, lat, lon)
    print(result)
