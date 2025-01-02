import tkinter as tk
from tkinter import filedialog, messagebox
import pdfplumber
import pytesseract
import cv2
import openai
import re
import os
import os
# Load OpenAI API Key securely from environment variable
openai.api_key =os.getenv('OPENAI_API_KEY') 
  # Ensure the environment variable is set

# Function for extracting text from a PDF
def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                else:
                    image = page.to_image()
                    ocr_text = pytesseract.image_to_string(image.original)
                    text += ocr_text
        return text
    except Exception as e:
        messagebox.showerror("Error", f"Error extracting text from PDF: {str(e)}")
        return ""

# Function for extracting text from an image
def extract_text_from_image(image_path):
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text = pytesseract.image_to_string(binary_image, config='--psm 6')
        return text
    except Exception as e:
        messagebox.showerror("Error", f"Error extracting text from image: {str(e)}")
        return ""

# Function to upload a file and extract text
def upload_file():
    global document_text
    file_path = filedialog.askopenfilename(filetypes=[("Supported files", "*.pdf *.jpg *.png *.jpeg")])
    if file_path:
        file_type = file_path.split('.')[-1].lower()
        extracted_text = extract_text_from_pdf(file_path) if file_type == 'pdf' else extract_text_from_image(file_path)

        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, extracted_text)

        document_text = extracted_text  # Store the extracted document text globally
    else:
        messagebox.showwarning("No File Selected", "Please select a PDF or image file.")

# Function to use OpenAI API for extracting relevant information
def get_answer_from_openai(extracted_text):
    if not extracted_text.strip():
        messagebox.showwarning("Empty Document", "No text found to process. Please upload a valid file.")
        return
    
    # Prompt for OpenAI API
    prompt = f"""
    You are an AI agent that takes text of bills as input and extracts relevant information.
    Use the fields under 'FIELDS' to parse the input text provided under 'INPUT'.
    
    FIELDS = {{
    "invoice number": "number/alphabets",
    "Item": "coffee/juice/burger/drinks",
    "QTY": "numbers in ML/L/KG",
    "Price": "number",
    "Amount": "total of bill"
    }}
    
    INPUT = """ + extracted_text + """
    
    Provide the extracted information in the following format:
    "invoice number", "Item", "QTY", "Price", "Amount"
    12345, Coffee, 1pc, $5.00, $5.00
    """
    try:
        # Ensure OpenAI response syntax is updated
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.2
        )
        result = response.choices[0].message['content'].strip()
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, result)
    except Exception as e:
        messagebox.showerror("API Error", f"Error calling OpenAI API: {str(e)}")

# Tkinter UI setup
root = tk.Tk()
root.title("Text Extraction and OpenAI Integration")

# Text area for displaying extracted text
text_area = tk.Text(root, wrap='word', height=20, width=80)
text_area.pack(padx=10, pady=10)

# Button to upload file
upload_button = tk.Button(root, text="Upload PDF/Image", command=upload_file)
upload_button.pack(pady=10)

# Button to get OpenAI response
openai_button = tk.Button(root, text="Extract Information", 
                          command=lambda: get_answer_from_openai(document_text))
openai_button.pack(pady=10)

root.mainloop()
