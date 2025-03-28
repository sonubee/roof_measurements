import googlemaps
import os
import requests
import json

class SolarAPI:
         
    def get_roof_dim(lat, lon, API_KEY):
    
        # Define parameters as in your working curl command
        params = {
            "location.latitude": lat,
            "location.longitude": lon,
            "requiredQuality": "HIGH",
            "key": API_KEY
        }

        # Endpoint for the Solar Building Insights API's findClosest method
        url = "https://solar.googleapis.com/v1/buildingInsights:findClosest"

        # Send the GET request with query parameters
        response = requests.get(url, params=params)
        
        # Check for success and print the results
        if response.status_code == 200:
            data = response.json()
             # Extract wholeRoofStats and the areaMeters2 value
            solarPotential = data.get("solarPotential", {})
            whole_roof_stats = solarPotential.get("wholeRoofStats", {})
            area_meters2 = whole_roof_stats.get("areaMeters2")
            print(f"Roof area in square meters: {area_meters2}")
             # Save the JSON data to a file
            with open("output.json", "w") as outfile:
                json.dump(solarPotential, outfile, indent=2)
        else:
            print("Error:", response.status_code)
            print(response.text)