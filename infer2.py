import requests
import cv2
from PIL import Image
from roboflow import Roboflow
import os
import json
from inference_sdk import InferenceHTTPClient

class Infer_Pic:

    def infer_krzak(filename):
        
        # Initialize the inference client with your API key and endpoint.
        client = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key="WC65G8Eh1ol0B7Aub5oW"
        )

        # Run the workflow to get predictions for your image.
        result = client.run_workflow(
            workspace_name="open-cities",
            workflow_id="detect-count-and-visualize",
            images={"image": "ce7c8043-bba1-44d9-99c5-b3e728b3812d.jpg"},
            use_cache=True  # caches workflow definition for 15 minutes
        )

        # Print the result to inspect the JSON output.
        print("Inference result:")
        print(result)

        # Load the original image locally using OpenCV.
        image = cv2.imread("ce7c8043-bba1-44d9-99c5-b3e728b3812d.jpg")
        if image is None:
            raise ValueError("Failed to load image. Please check the file path.")

        # Assume the result JSON contains a "predictions" key with a list of predictions.
        predictions = result.get("predictions", [])
        print(f"Found {len(predictions)} predictions.")

        # Loop over each prediction to draw bounding boxes and labels.
        for pred in predictions:
            # Expected format for each prediction (adjust if necessary):
            # {
            #   "x": <x-coordinate>,
            #   "y": <y-coordinate>,
            #   "width": <width>,
            #   "height": <height>,
            #   "class": "<label>",
            #   "confidence": <confidence score>
            # }
            x = int(pred.get("x", 0))
            y = int(pred.get("y", 0))
            width = int(pred.get("width", 0))
            height = int(pred.get("height", 0))
            label = f"{pred.get('class', 'object')} {pred.get('confidence', 0):.2f}"

            # Draw the bounding box.
            cv2.rectangle(image, (x, y), (x + width, y + height), (0, 255, 0), 2)
            # Draw the label above the box.
            cv2.putText(image, label, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Save the annotated image.
        annotated_path = "annotated_output.jpg"
        cv2.imwrite(annotated_path, image)
        print(f"Annotated image saved as {annotated_path}")

        # Optionally, display the annotated image.
        cv2.imshow("Annotated Image", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()