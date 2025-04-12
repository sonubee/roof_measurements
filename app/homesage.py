import requests
import json
from get_keys import Get_Keys
import os

class HomeSage:

    def return_roof(address):
        headers = Get_Keys.get_homesage()

        response = requests.get('https://developers.homesage.ai/api/properties/info/', headers=headers, params={'property_address': {address}})

        # For some reason Python can't read roof directly from json so I am saving to a file, then reading from file, then deleteing file
        if response.status_code == 200:
            data = response.json()
            buildingInfo = data.get("building_info", {})
            print("Roof: ",  data.get("roof"))
            print(buildingInfo)
            
            with open("roof.json", 'w') as f:
                json.dump(buildingInfo, f, indent=4)  # Save with indentation for readability
            
            with open("roof.json", 'r') as file:
                data2 = json.load(file)
                file.close()
                os.remove("roof.json")
                return data2.get("roof")