import uuid
import requests

class Sat_Image:

    def download_google_maps_satellite(lat, lon):
        """
        Downloads a high-resolution satellite image from Google Static Maps API.
        """
        API_KEY = "AIzaSyBPl2BN22N1olCSEKphDwv822foR4PlYF4"  # Replace with your API key
        ZOOM = 20  # Max zoom for high detail (adjust if needed)
        SIZE = "640x640"  # Max image size (you can stitch multiple images for ultra-high res)
        MAP_TYPE = "satellite"
        
        filename = Sat_Image.generate_unique_id()
        filename = filename + ".png"

        url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={ZOOM}&size={SIZE}&maptype={MAP_TYPE}&key={API_KEY}"

        response = requests.get(url)

        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"High-resolution image saved as {filename}")
        else:
            print("Error downloading image:", response.status_code)
            
        return filename
        
    def generate_unique_id():
        """Generates a unique ID using uuid4."""
        return str(uuid.uuid4())