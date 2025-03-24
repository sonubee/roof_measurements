import requests
import json

# Replace these with your actual values
API_KEY = "WC65G8Eh1ol0B7Aub5oW"
WORKSPACE = "open-cities"           # e.g. "my-workspace"
PROJECT = "my-first-project-bt5zl"          # e.g. "roof-detection"

# Construct the URL to get project details
url = f"https://api.roboflow.com/{WORKSPACE}/{PROJECT}?api_key={API_KEY}"

response = requests.get(url)
if response.status_code == 200:
    project_data = response.json()
    # Print the entire JSON nicely formatted
    print(json.dumps(project_data, indent=2))
    
    # Optionally, if the JSON has a "versions" key, you can print just that:
    if "versions" in project_data:
        print("\nModel Versions:")
        for version in project_data["versions"]:
            print(f"Version: {version.get('id')} - Published: {version.get('published')}")
    else:
        print("No version information found in the project data.")
else:
    print("Error fetching project details:")
    print(response.status_code, response.text)
