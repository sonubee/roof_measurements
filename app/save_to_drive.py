import ee
import uuid
from get_keys import Get_Keys

class ToDrive:

    service_account, file_loc = Get_Keys.get_service_account()
    credentials = ee.ServiceAccountCredentials(service_account, file_loc)
    ee.Initialize(credentials)

    def save_raw_image_to_drive(lat, lon, address):
        filename = address
        print(lat, " + ", lon)

        # Define the point for the house location
        point = ee.Geometry.Point(lon, lat)

        # Use NAIP imagery (USA only, 1m resolution)
        collection = ee.ImageCollection("USDA/NAIP/DOQQ") \
            .filterBounds(point) \
            .filterDate("2022-01-01", "2024-12-31") \
            .sort("system:time_start", False)  # Get latest image

        latest_image = collection.first()

        # Select RGB bands (NAIP bands are ["R", "G", "B", "N"])
        roof_image = latest_image.select(["R", "G", "B"])

        # Define export region (increase buffer for larger area)
        region = point.buffer(15).bounds()  # Adjust based on house size

        # Export image to Google Drive
        task = ee.batch.Export.image.toDrive(
            image=roof_image.toUint16(),
            description=filename,
            folder="EarthEngineExports",
            fileNamePrefix=filename,
            scale=1,  # 1m resolution
            region=region,
            fileFormat="GEO_TIFF"
        )
        
        # Start the export task
        task.start()
        
        print("Export started: Image will be available in Google Drive folder 'EarthEngineExports' as ", filename, ".tif")

        return f"Export started: Image will be available in Google Drive folder 'EarthEngineExports' as {filename}.tif"