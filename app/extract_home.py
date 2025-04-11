import cv2
import json
import numpy as np
import math

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
        cropped_buffer, cropped_roof = Extract_Now.crop_roof_and_buffer(image, best_pts, buffer=60)

        # Save the results.
        cv2.imwrite("cropped_buffer.png", cropped_buffer)
        cv2.imwrite("cropped_roof.png", cropped_roof)
        print("Saved 'cropped_buffer.png' (full buffered image) and 'cropped_roof.png' (roof-only image).")

    # Now, crop the roof using the best_prediction's polygon points
    def crop_roof_and_buffer(image, polygon_points, buffer=60):
        """
        Extracts two regions from an image based on polygon points:
          1. The full buffered region (surroundings plus roof)
          2. The roof-only region (mask applied) within that buffer.
        
        Parameters:
            image (np.ndarray): The original image.
            polygon_points (list): List of (x, y) tuples defining the roof polygon.
            buffer (int): Buffer size in pixels to add around the polygon.
            
        Returns:
            tuple: (cropped_buffer, cropped_roof) where:
                - cropped_buffer is the original image crop with the buffer,
                - cropped_roof is the same crop but with the non-roof area masked out.
        """
        # Convert polygon points to a NumPy array in the shape required by OpenCV.
        pts = np.array(polygon_points, np.int32).reshape((-1, 1, 2))
        
        # Compute the bounding rectangle of the polygon.
        x, y, w, h = cv2.boundingRect(pts)
        
        # Expand the bounding box by the buffer value.
        x_buf = max(x - buffer, 0)
        y_buf = max(y - buffer, 0)
        x2_buf = min(x + w + buffer, image.shape[1])
        y2_buf = min(y + h + buffer, image.shape[0])
        
        # Crop the entire buffered region from the original image.
        cropped_buffer = image[y_buf:y2_buf, x_buf:x2_buf]
        
        # Create a mask for the roof polygon.
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)
        
        # Apply the mask to the image to isolate the roof.
        roof_only = cv2.bitwise_and(image, image, mask=mask)
        
        # Crop the same buffered region from the masked roof image.
        cropped_roof = roof_only[y_buf:y2_buf, x_buf:x2_buf]
        
        return cropped_buffer, cropped_roof