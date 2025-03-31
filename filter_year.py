import pandas as pd

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
