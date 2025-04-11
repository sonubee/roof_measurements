import pandas as pd
from homesage import HomeSage
import json
import csv

# Read the file (change to read_excel if needed)
# For CSV:
df = pd.read_excel("sac_county_secured_roll_public.xlsx")

# If it's an Excel file, uncomment the following line and comment the read_csv line:
# df = pd.read_excel("San Carlos Way Farm.xlsx - SiteXProListOrdersExcelReport.xlsx")

print("here0")

# Combine "Property Address", "City", and "State" into one field "Full Address"
# Convert to string in case there are non-string values
df["Site Address"] = df["SITUS_NUMBER"].astype(str) + " " + df["SITUS_STREET"].astype(str) + ". " + df["SITUS_CITY"].astype(str) + ", CA. " + df["SITUS_ZIP"].astype(str)
df["Mailing Address"] = df["MAIL_ADDRESS"].astype(str) + ". " + df["MAIL_CITY"].astype(str) + ", CA. " + df["MAIL_ZIP"].astype(str)

print("here1")

# Create a new DataFrame with only the relevant columns:
# "Full Address" and "Year Built"
result_df = df[["Site Address", "Mailing Address", "OWNER", "ZONING"]].copy()

print("here2")

output_filename = "all_sac_homes.xlsx"
result_df.to_excel(output_filename, index=False)
print(f"DataFrame saved to {output_filename}")