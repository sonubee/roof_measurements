from fpdf import FPDF
from PIL import Image

class Property_Report:

    def gen_report(property_address, roof_measurement, latitude, longitude, satellite_image, annotated_polygon, cropped_buffer, roofType):

        # Create a PDF class instance
        pdf = FPDF()
        pdf.add_page()

        # Set title and heading fonts
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Property Report", ln=True, align="C")
        pdf.ln(10)

        # Set normal text font for details
        pdf.set_font("Arial", "", 12)

        # Write the details to the PDF
        pdf.cell(0, 10, f"Address: {property_address}", ln=True)
        pdf.cell(0, 10, "Roof Measurement: " + str(roof_measurement) + " m²", ln=True)
        pdf.cell(0, 10, "Latitude: " + str(latitude), ln=True)
        pdf.cell(0, 10, "Longitude: " + str(longitude), ln=True)
        pdf.cell(0, 10, "Roof Type: " + str(roofType), ln=True)
        pdf.ln(10)

        # Define image file paths (update these with your actual file names)
        # satellite_image = "satellite_image.jpg"
        # annotated_polygon = "annotated_polygon.jpg"
        # cropped_buffer = "cropped_buffer.png"
        
        img = Image.open(satellite_image)
        # Save it as a new PNG file with correct formatting
        img.save(satellite_image, "PNG")

        # Add the Satellite Image
        pdf.cell(0, 10, "Satellite Image:", ln=True)
        # Adjust x, y, and width as needed (here we leave a 10mm margin)
        pdf.image(satellite_image, x=10, y=pdf.get_y(), w=pdf.w - 100)
        pdf.ln(200)  # Adjust vertical spacing based on image height

        # Add the Annotated Polygon Image
        pdf.cell(0, 10, "Annotated Polygon:", ln=True)
        pdf.image(annotated_polygon, x=10, y=pdf.get_y(), w=pdf.w - 100)
        pdf.ln(115)  # Adjust spacing as needed

        # Add the Cropped Buffer Image
        pdf.cell(0, 10, "Cropped Buffer:", ln=True)
        pdf.image(cropped_buffer, x=10, y=pdf.get_y(), w=pdf.w - 140)
        pdf.ln(165)

        # Save the PDF to a file
        pdf.output(property_address + ".pdf")
        print("PDF report saved as " + property_address + ".pdf")
