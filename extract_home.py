import cv2
import json
import numpy as np
import math

class Extract_House:

    # --- Helper Functions ---

    def haversine(lat1, lon1, lat2, lon2):
        """Calculate the Haversine distance in meters between two geographic points."""
        R = 6371000  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi/2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def pixel_to_latlon(px, py, center_lat, center_lon, zoom, img_width, img_height):
        """
        Convert pixel coordinates (px,py) on a static map to geographic coordinates.
        This function uses an approximate conversion for Google Maps' Mercator projection.
        """
        # Calculate meters per pixel at the given zoom level (approximation)
        # 156543.03392 meters per pixel at zoom 0 at the equator
        meters_per_pixel = 156543.03392 * math.cos(math.radians(center_lat)) / (2 ** zoom)
        
        # Assume the center of the image is at (img_width/2, img_height/2)
        dx = px - img_width / 2.0  # positive dx means eastward
        dy = py - img_height / 2.0 # positive dy means southward

        # Calculate offset in meters
        offset_east = dx * meters_per_pixel
        offset_north = -dy * meters_per_pixel  # negative because pixel y increases downward

        # Convert meter offsets to lat/lon differences
        delta_lat = (offset_north / 6378137) * (180 / math.pi)  # Earth's radius in meters
        delta_lon = (offset_east / (6378137 * math.cos(math.radians(center_lat)))) * (180 / math.pi)
        
        return center_lat + delta_lat, center_lon + delta_lon

    def polygon_centroid(points):
        """
        Compute the centroid of a polygon given as a list of (x, y) points.
        Uses the standard formula for the centroid of a polygon.
        """
        if len(points) == 0:
            return (0, 0)
        x_list = [p[0] for p in points]
        y_list = [p[1] for p in points]
        length = len(points)
        return (sum(x_list) / length, sum(y_list) / length)

class Extract_Now:

    # --- Main Code ---
    
    def start_work(map_filename, lat, lon):

        # Load your prediction JSON file (replace with your file name)
        with open("output_prediction.json", "r") as f:
            predictions_data = json.load(f)

        # Load the image that was used for inference
        # (Assuming this image is the one you got from, e.g., Google Static Maps)
        image = cv2.imread(map_filename)
        if image is None:
            raise ValueError("Image file not found.")

        img_height, img_width = image.shape[:2]

        # Define the parameters for the static map:
        # These values should match those you used when requesting the image.
        center_lat = lat
        center_lon = lon
        zoom = 18  # For example; adjust as needed

        # Assume predictions_data["predictions"] is a list of predictions.
        predictions = predictions_data.get("predictions", [])

        # Now, for each prediction, compute the centroid (in pixel coordinates)
        # and convert that to geographic coordinates.
        best_prediction = None
        min_distance = float("inf")

        for pred in predictions:
            if "points" in pred and pred["points"]:
                # Get polygon points as a list of (x, y) tuples
                pts = [(point["x"], point["y"]) for point in pred["points"]]
                # Compute the centroid in pixel space
                centroid_px = Extract_House.polygon_centroid(pts)
                # Convert pixel centroid to lat/lon using our conversion function
                pred_lat, pred_lon = Extract_House.pixel_to_latlon(
                    centroid_px[0], centroid_px[1],
                    center_lat, center_lon,
                    zoom, img_width, img_height
                )
                # Compute the distance between this prediction's centroid and the input coordinates
                dist = Extract_House.haversine(center_lat, center_lon, pred_lat, pred_lon)
                # Debug: print the computed geographic centroid and distance
                print(f"Prediction {pred.get('detection_id')} centroid: ({pred_lat:.6f}, {pred_lon:.6f}), distance: {dist:.2f} m")
                
                if dist < min_distance:
                    min_distance = dist
                    best_prediction = pred

        if best_prediction is None:
            raise ValueError("No valid predictions with polygon points found.")

        print(f"Selected prediction {best_prediction.get('detection_id')} with distance {min_distance:.2f} m")
        
        # Use the best prediction's polygon to crop the roof area
        best_pts = [(int(p["x"]), int(p["y"])) for p in best_prediction["points"]]
        roof_crop = Extract_Now.crop_roof(image, best_pts)

        # Save and show the cropped roof image
        cropped_filename = "cropped_roof.png"
        cv2.imwrite(cropped_filename, roof_crop)
        print(f"Cropped roof image saved as {cropped_filename}")

    # Now, crop the roof using the best_prediction's polygon points
    def crop_roof(image, polygon_points):
        # Create a blank mask (same dimensions as the image)
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        pts = np.array(polygon_points, np.int32).reshape((-1, 1, 2))
        cv2.fillPoly(mask, [pts], 255)
        # Apply the mask to the image
        roof_only = cv2.bitwise_and(image, image, mask=mask)
        # Optionally, compute the bounding rect of the polygon and crop that region
        x, y, w, h = cv2.boundingRect(pts)
        cropped_roi = roof_only[y:y+h, x:x+w]
        return cropped_roi
