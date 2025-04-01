import requests
import json

class HomeSage:

    def return_roof(address):
        headers = {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjcwMGZkYjFkLWE0MjgtNDI4Yi04ODc1LTliZGU0MGMwN2QzNyIsImV4cCI6MTc1MTE0Njg0NjUuMDk3NzV9._ev4p-bSaARxdYneTFDFX_N1PCPus9sxuRotKkqdQjQ'
        }

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