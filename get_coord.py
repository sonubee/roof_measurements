import requests

class Geocoding:

    def get_lat_lon(address, api_key):
        """
        Get the latitude and longitude for a given address using the Google Maps Geocoding API.
        
        Args:
            address (str): The address to geocode.
            api_key (str): Your Google Maps API key.
        
        Returns:
            tuple: (latitude, longitude) if found, else (None, None).
        """
        base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": api_key
        }
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "OK" and data["results"]:
                location = data["results"][0]["geometry"]["location"]
                return location["lat"], location["lng"]
            else:
                print("Geocoding error:", data.get("status"), data.get("error_message"))
                return None, None
        else:
            print("HTTP error:", response.status_code)
            return None, None