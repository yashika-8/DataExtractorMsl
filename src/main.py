import openai
import yaml
import os
from tkinter import messagebox
from utils import extract_text_from_pdf, Make_Prompt


def load_api_key():
    try:
        with open('config.yaml', 'r') as config_file:
            config = yaml.safe_load(config_file)
            return config['openai_api_key']
    except Exception as e:
        messagebox.showerror("Error", f"Error loading API key: {str(e)}")
        return None


def extract_information_from_bill(file_path, question):
    openai.api_key = load_api_key()
    if openai.api_key is None:
        return "API Key not found!"

    # Extract text from PDF
    extracted_text = extract_text_from_pdf(file_path)
    if not extracted_text:
        return "Could not extract text from the provided bill."

    # Create the prompt for OpenAI API
    prompt = Make_Prompt(extracted_text, question)

    # Call OpenAI API to get the result
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        messagebox.showerror("Error", f"Error in API request: {str(e)}")
        return None


def main():
    # You would call the function with the user's file and question like this:
    file_path = "path_to_your_pdf.pdf"  # Replace with the path to your bill PDF
    question = "What is the quantity of coffee?"

    result = extract_information_from_bill(file_path, question)
    print("Result:", result)


if __name__ == "__main__":
    main()
