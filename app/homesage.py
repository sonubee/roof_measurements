import requests
import json
from get_keys import Get_Keys

class HomeSage:

    def return_roof(address):
        headers = Get_Keys.get_homesage()

        response = requests.get('https://developers.homesage.ai/api/properties/info/', headers=headers, params={'property_address': '3916 San Carlos Way Sacramento, CA'})

        if response.status_code == 200:
            # print(response.json())
            data = response.json()
            buildingInfo = data.get("building_info", {})
            
            with open("roof.json", 'w') as f:
                json.dump(buildingInfo, f, indent=4)  # Save with indentation for readability
            
            with open("roof.json", 'r') as file:
                data2 = json.load(file)
                return data2.get("roof")