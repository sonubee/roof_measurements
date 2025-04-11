import os

class Random_Function

    def path_of_db:
        # Find the absolute path of quotes.db
    db_path = os.path.abspath("instance/quotes.db")
    print("Full path of your database:", db_path)
    
    '''
# Route to Generate Quote
@app.route("/generate", methods=["POST"])
def generate():
    customer_name = request.form["customer_name"]
    recipient_email = request.form["recipient_email"]
    product_details = request.form["product_details"]
    price = float(request.form["price"])
    validity = int(request.form["validity"])

    # Generate AI-powered email
    email_content = Open.generate_quote_email(customer_name, product_details, price, validity)
    
    # Generate PDF
    pdf_filename = GenPDF.generate_pdf_quote(customer_name, product_details, price, validity)

    # Store Quote in Database
    new_quote = Quote(
        customer_name=customer_name,
        recipient_email=recipient_email,
        product_details=product_details,
        price=price,
        validity=validity,
        pdf_filename=pdf_filename
        )
    db.session.add(new_quote)    
    db.session.commit()
        
    #Send Email with PDf    
    Email.send_email_with_pdf(recipient_email, "Your Quote", email_content, pdf_filename)
    
    # Example usage:
    address = "3972 Myinda Dr. San Jose, CA. 95132"
    api_key = ""  
    lat, lon = Geocoding.get_lat_lon(address, api_key)
    print(f"Latitude: {lat}, Longitude: {lon}")
    
    map_filename = Sat_Image.download_google_maps_satellite(lat, lon)
    Infer_Pic.infer_krzak(map_filename) 
    
    return "This is a valid response"  # Return a string


# Route to View & Download Images
@app.route("/images")
def list_images():
    quotes = Quote.query.all()
    return render_template("images.html", quotes=quotes)

@app.route("/download/<filename>")
def download_image(filename):
    """Download an image from the static/images directory."""
    file_path = os.path.join("static/images", filename)
    return send_file(file_path, as_attachment=True)
'''
