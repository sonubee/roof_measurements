from fpdf import FPDF

class GenPDF:
    # Function to generate PDF quote
    def generate_pdf_quote(customer_name, product_details, price, validity):
        filename = f"quote_{customer_name.replace(' ', '_')}.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Quotation", ln=True, align="C")
        pdf.ln(10)
        
        pdf.cell(200, 10, txt=f"Customer: {customer_name}", ln=True)
        pdf.cell(200, 10, txt=f"Product/Service: {product_details}", ln=True)
        pdf.cell(200, 10, txt=f"Price: ${price}", ln=True)
        pdf.cell(200, 10, txt=f"Quote Validity: {validity} days", ln=True)

        pdf.output(filename)
        return filename