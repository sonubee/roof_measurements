from osgeo import gdal
import sys

def convert_geotiff_to_png(input_tif, output_png):
    """
    Converts a GeoTIFF file to PNG format.
    
    Args:
        input_tif (str): Path to the GeoTIFF file.
        output_png (str): Path to save the PNG file.
    """
    dataset = gdal.Open(input_tif)
    if not dataset:
        print("Error: Could not open GeoTIFF file.")
        sys.exit(1)

    gdal.Translate(output_png, dataset, format="PNG")
    print(f"Converted {input_tif} to {output_png}")

# Example Usage
convert_geotiff_to_png("3aff8715-3707-4dd6-9ef9-9acaf5331584.tif", "3aff8715-3707-4dd6-9ef9-9acaf5331584.png")