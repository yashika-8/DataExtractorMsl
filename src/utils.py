import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    try:
        # Open the PDF file
        doc = fitz.open(pdf_path)
        
        # Initialize an empty string to store the extracted text
        text = ""
        
        # Loop through all pages in the PDF
        for page_num in range(doc.page_count):
            # Load the page
            page = doc.load_page(page_num)
            
            # Extract text from the page
            text += page.get_text("text")  # You can choose other formats like "html", "json", etc.
        
        # Return the extracted text
        return text
    
    except Exception as e:
        # Print error message if any issues occur
        print(f"Error extracting text: {str(e)}")
        return None
