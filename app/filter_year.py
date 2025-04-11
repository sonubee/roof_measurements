import pandas as pd
from homesage import HomeSage
import json
import csv

# Read the file (change to read_excel if needed)
# For CSV:
df = pd.read_csv("San Carlos Way Farm.xlsx - SiteXProListOrdersExcelReport.csv")

# If it's an Excel file, uncomment the following line and comment the read_csv line:
# df = pd.read_excel("San Carlos Way Farm.xlsx - SiteXProListOrdersExcelReport.xlsx")

# Combine "Property Address", "City", and "State" into one field "Full Address"
# Convert to string in case there are non-string values
df["Full Address"] = df["Property Address"].astype(str) + ", " + df["City"].astype(str) + ", " + df["State"].astype(str)

# Create a new DataFrame with only the relevant columns:
# "Full Address" and "Year Built"
result_df = df[["Full Address", "Year Built"]].copy()

# Ensure that "Year Built" is numeric
result_df["Year Built"] = pd.to_numeric(result_df["Year Built"], errors="coerce")

# Filter properties built between 1980 and 1990 (inclusive)
filtered_df = result_df[result_df["Year Built"].between(1980, 1990, inclusive="both")]

# Output the filtered DataFrame to a JSON file (as a list of records)
filtered_df.to_json("properties_1980_1990.json", orient="records", indent=2)

print("Filtered JSON saved as properties_1980_1990.json")

with open("properties_1980_1990.json", "r") as file:
    data = json.load(file)

# roofType = HomeSage.return_roof(address)

for item in data:
    # Process each item in the list
    print(item)
    item["Roof Type"] = HomeSage.return_roof(item["Full Address"])
    print(item)
    
with open("properties_1980_1990.json", 'w') as file:
    json.dump(data, file, indent=4) # indent for better readability
    
    """
    Converts a JSON file to a CSV file.

    Args:
        json_filepath (str): Path to the input JSON file.
        csv_filepath (str): Path to the output CSV file.
    """
with open("properties_1980_1990.json", 'r') as json_file, open("dads_report.csv", 'w', newline='') as csv_file:
    data = json.load(json_file)
    writer = csv.writer(csv_file)
    
    if isinstance(data, list):
        if data:
            header = data[0].keys()
            writer.writerow(header)
            for row in data:
                writer.writerow(row.values())
    elif isinstance(data, dict):
        header = data.keys()
        writer.writerow(header)
        writer.writerow(data.values())
