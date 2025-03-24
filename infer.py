import requests
import cv2
from PIL import Image
from roboflow import Roboflow
import os
import json

class Infer_Pic:

    def infer_krzak(filename):

        api_key="WC65G8Eh1ol0B7Aub5oW"
        rf = Roboflow(api_key="WC65G8Eh1ol0B7Aub5oW")
       
        url = f"https://api.roboflow.com/?api_key={api_key}"

        response = requests.get(url)

        if response.status_code == 200:
            workspace_info = response.json()
            print("Active workspace info:")
            print(workspace_info)
        else:
            print("Error:", response.status_code, response.text)
       
        # Access your workspace and project (replace with your actual project name)
        project = rf.workspace().project("my-first-project-bt5zl")
        print("hello1")
        print(project)
        print("hello2")
        # Select the version of your model you wish to use (replace 1 with your version number)
        model = project.version(3).model
        print("hello3")
        workspace = rf.workspace()
        print("Workspace:", workspace)
        print("hello5")
        # Replace 'your-project-name' with the exact project name from your dashboard.
        project = workspace.project("krzak")
        print("Project:", project)
        
        # Load your image
        img = Image.open(filename)

        # Check the mode and convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Save as JPEG
        print("hello6")

        
        if filename.lower().endswith(".png"):
            new_filename = os.path.splitext(filename)[0] + ".jpg"
            os.rename(filename, new_filename)
            print(f"Renamed '{filename}' to '{new_filename}'")
        else:
            print(f"'{filename}' is not a PNG file.")
        
        img.save(filename, "JPEG")

        # Check if the version exists
        try:
            model = project.version(1).model
            print("Model loaded successfully:", model)
        except Exception as e:
            print("Error loading model:", e)
            
        # Local or URL image
        prediction = model.predict(filename).json()
        
        '''
        # Function to read a local json file. Only for testing
        with open('pred_returned.json', 'r') as file:
            # The 'with' statement ensures the file is automatically closed
            # even if errors occur.
            prediction = json.load(file)
        '''
        
        print(prediction)
        
        image_path = filename  # Replace with your image file path
        image = cv2.imread(image_path)
        
        # Draw bounding boxes and labels on the image
        for pred in prediction.get("predictions", []):
            x = int(pred["x"])
            y = int(pred["y"])
            w = int(pred["width"])
            h = int(pred["height"])
            label = f"{pred['class']} {pred['confidence']:.2f}"
            
            # Draw rectangle (bounding box)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # Draw label above the rectangle
            cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)
     
        # Save the annotated image
        annotated_image_path = "annotated_output.jpg"
        cv2.imwrite(annotated_image_path, image)
        print(f"Annotated image saved as {annotated_image_path}")