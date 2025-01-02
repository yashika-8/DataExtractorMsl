import tkinter as tk
from tkinter import filedialog, messagebox
import pdfplumber
import pytesseract
import cv2
from transformers import pipeline


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
    file_path = filedialog.askopenfilename(filetypes=[("Supported files", "*.pdf *.jpg *.png *.jpeg")])
    if file_path:
        file_type = file_path.split('.')[-1].lower()
        extracted_text = extract_text_from_pdf(file_path) if file_type == 'pdf' else extract_text_from_image(file_path)

        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, extracted_text)

        global document_text
        document_text = extracted_text  # Store the extracted document text globally


# Function to answer questions from the document
def answer_question():
    try:
        question = question_entry.get()
        if not question:
            messagebox.showwarning("Input Error", "Please enter a question.")
            return

        if not document_text:
            messagebox.showerror("Error", "Please upload a document first.")
            return

        # Load the question-answering model
        qa_model = pipeline('question-answering', model='distilbert-base-uncased-distilled-squad')

        # Get the answer from the document
        result = qa_model(question=question, context=document_text)
        answer = result['answer']

        # Display the answer
        answer_area.delete(1.0, tk.END)
        answer_area.insert(tk.END, f"Question: {question}\nAnswer: {answer}")

    except Exception as e:
        messagebox.showerror("Error", f"Error answering question: {str(e)}")


# Initialize the GUI
root = tk.Tk()
root.title("Document Q&A System")

upload_button = tk.Button(root, text="Upload File", command=upload_file)
upload_button.pack()

text_area = tk.Text(root, height=10, width=60)
text_area.pack()

question_label = tk.Label(root, text="Enter your question:")
question_label.pack()

question_entry = tk.Entry(root, width=50)
question_entry.pack()

ask_button = tk.Button(root, text="Ask Question", command=answer_question)
ask_button.pack()

answer_area = tk.Text(root, height=10, width=60)
answer_area.pack()

root.mainloop()