import requests
import cv2
from PIL import Image
from roboflow import Roboflow
from io import BytesIO
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from get_keys import Get_Keys

class Infer_Pic:

    def infer_krzak(filename):
        
        model_version = 4

        api_key=Get_Keys.get_roboflow_key()
        rf = Roboflow(api_key)
       
        url = f"https://api.roboflow.com/?api_key={api_key}"

        response = requests.get(url)

        if response.status_code == 200:
            workspace_info = response.json()
        else:
            print("Error:", response.status_code, response.text)
       
        # Access your workspace and project (replace with your actual project name)
        project = rf.workspace().project("roof-detection-dym1x")
   
        # Select the version of your model you wish to use (replace 1 with your version number)
        model = project.version(model_version).model
        workspace = rf.workspace()
        
        # Load your image
        img = Image.open(filename)

        # Check the mode and convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")
            print("changed to RGB")

        # Save as JPEG

        if filename.lower().endswith(".png"):
            new_filename = os.path.splitext(filename)[0] + ".jpg"
            os.replace(filename, new_filename)
        else:
            print(f"'{filename}' is not a PNG file.")
        
        img.save(filename, "JPEG")

        # Check if the version exists
        try:
            model = project.version(model_version).model
            print("Model loaded successfully:", model)
        except Exception as e:
            print("Error loading model:", e)
            
        # Local or URL image
        prediction = model.predict(filename).json()
        
        print("did it predict?")
        
        with open("output_prediction.json", "w") as outfile:
                json.dump(prediction, outfile, indent=2)
       
        # Load the prediction JSON file
        with open("output_prediction.json", "r") as f:
            predictions_data = json.load(f)

        # Load the image on which the predictions were made.
        # (Make sure the file name here matches the image used for inference.)
        # image = cv2.imread("3d8ff972-4a4b-4e25-bdfd-dbaf7a225b06.png")
        image = cv2.imread(filename)
        if image is None:
            raise ValueError("Image file not found.")

        # Loop over each prediction
        for pred in predictions_data.get("predictions", []):
            # Check if the prediction contains polygon points
            if "points" in pred and pred["points"]:
                # Convert the list of dict points to a list of tuples of integers
                pts = [(int(point["x"]), int(point["y"])) for point in pred["points"]]
                
                # Convert the list of points into a NumPy array of shape (n,1,2)
                pts_array = np.array(pts, np.int32).reshape((-1, 1, 2))
                
                # Draw the polygon outline on the image (red color, thickness 2)
                cv2.polylines(image, [pts_array], isClosed=True, color=(0, 0, 255), thickness=2)
                
                # Optionally, fill the polygon with a semi-transparent overlay
                overlay = image.copy()
                cv2.fillPoly(overlay, [pts_array], color=(0, 0, 255))
                alpha = 0.3  # Transparency factor
                cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
                
                # Optionally, draw a label (e.g., class name and confidence)
                label = f"{pred.get('class', 'object')} {pred.get('confidence', 0):.2f}"
                # Place the label at the first point of the polygon
                cv2.putText(image, label, pts[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            else:
                print("No polygon points for prediction with detection_id:",
                      pred.get("detection_id", "unknown"))

        # Save the annotated image
        output_filename = "annotated_polygon.jpg"
        cv2.imwrite(output_filename, image)
        print(f"Annotated image saved as {output_filename}")
        
    def infer_roof(pil_image):
        
        model_version = 4

        api_key=Get_Keys.get_roboflow_key()
        rf = Roboflow(api_key)
       
        url = f"https://api.roboflow.com/?api_key={api_key}"

        response = requests.get(url)

        if response.status_code == 200:
            workspace_info = response.json()
        else:
            print("Error:", response.status_code, response.text)
       
        # Access your workspace and project (replace with your actual project name)
        project = rf.workspace().project("roof-detection-dym1x")
   
        # Select the version of your model you wish to use (replace 1 with your version number)
        model = project.version(model_version).model
        workspace = rf.workspace()
        
        # Load your image
        # img = image
        
        '''
        # Check the mode and convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Save as JPEG

        if filename.lower().endswith(".png"):
            new_filename = os.path.splitext(filename)[0] + ".jpg"
            os.replace(filename, new_filename)
        else:
            print(f"'{filename}' is not a PNG file.")
        
        img.save(filename, "JPEG")
        '''
        
        '''
        # Open and convert the image to RGB
        pil_image = Image.open(BytesIO(image)).convert("RGB")

        # Convert to a numpy array with explicit data type
        image_np = np.array(pil_image, dtype=np.uint8)
        
        
        # Optionally, convert the PIL Image to a NumPy array.
        # This is useful if your Roboflow model accepts numpy arrays.
        image_np = np.array(pil_image)
        '''
        
        # Check if the version exists
        try:
            model = project.version(model_version).model
            print("Model loaded successfully:", model)
        except Exception as e:
            print("Error loading model:", e)
            
        print("before prediction infer_roof")
        print(pil_image)
        print("after printing array")
        # Local or URL image
        prediction = model.predict(pil_image).json()
        print("not here")
        
        with open("output_prediction.json", "w") as outfile:
                json.dump(prediction, outfile, indent=2)
       
        # Load the prediction JSON file
        with open("output_prediction.json", "r") as f:
            predictions_data = json.load(f)
        '''
        # Load the image on which the predictions were made.
        # (Make sure the file name here matches the image used for inference.)
        # image = cv2.imread("3d8ff972-4a4b-4e25-bdfd-dbaf7a225b06.png")
        image = cv2.imread(new_filename)
        if image is None:
            raise ValueError("Image file not found.")
            
        '''
        
        print("Before pred in 2nd Google Map image")
        
        # Loop over each prediction
        for pred in predictions_data.get("predictions", []):
            # Check if the prediction contains polygon points
            if "points" in pred and pred["points"]:
                # Convert the list of dict points to a list of tuples of integers
                pts = [(int(point["x"]), int(point["y"])) for point in pred["points"]]
                
                # Convert thSe list of points into a NumPy array of shape (n,1,2)
                pts_array = np.array(pts, np.int32).reshape((-1, 1, 2))
                
                # Draw the polygon outline on the image (red color, thickness 2)
                cv2.polylines(image, [pts_array], isClosed=True, color=(0, 0, 255), thickness=2)
                
                # Optionally, fill the polygon with a semi-transparent overlay
                overlay = image.copy()
                cv2.fillPoly(overlay, [pts_array], color=(0, 0, 255))
                alpha = 0.3  # Transparency factor
                cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
                
                # Optionally, draw a label (e.g., class name and confidence)
                label = f"{pred.get('class', 'object')} {pred.get('confidence', 0):.2f}"
                # Place the label at the first point of the polygon
                cv2.putText(image, label, pts[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            else:
                print("No polygon points for prediction with detection_id:",
                      pred.get("detection_id", "unknown"))

        # Save the annotated image
        output_filename = "annotated_polygon2.jpg"
        cv2.imwrite(output_filename, image)
        print(f"Annotated image saved as {output_filename}")