import openai

class Open:

    # Function to generate AI-powered email
    def generate_quote_email(customer_name, product_details, price, validity):
        prompt = f"""
        Generate a professional email to {customer_name} for a quote.
        - Product/Service: {product_details}
        - Price: ${price}
        - Quote Validity: {validity} days
        The email should be polite, professional, and include a call to action.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4-turbo",  # Use "gpt-4-turbo" for cost-effective performance
            messages=[{"role": "system", "content": "You are a helpful assistant that writes professional emails."},
                      {"role": "user", "content": prompt}]
        )
    
        response_message = response.choices[0].message.content
        print(response_message )
        
        if hasattr(response.choices[0].message, "content"):
               print(response.choices[0].message)
        
        return response_message 