import os
import re
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
import json
from concurrent.futures import ThreadPoolExecutor

# Set the path to the Tesseract executable (update this with your path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

def extract_text_from_pdf(pdf_path):
    text = ''
    # Open the PDF file using PyMuPDF
    with fitz.open(pdf_path) as pdf_document:
        # Convert the entire PDF to images
        images = convert_from_path(pdf_path)

        # Use multithreading to process OCR concurrently
        with ThreadPoolExecutor() as executor:
            # Extract text from each image using OCR
            futures = [executor.submit(extract_text_from_image, image) for image in images]
            for future in futures:
                text += future.result()

    return text

def extract_property_address(text):
    # Define regular expression patterns to match different formats of property addresses
    patterns = [
        r'\[Property Address\]\s*(.+?)\n',
        r'\b(\d+\s+[A-Z]+\s*[A-Z]*,\s*[A-Z]+\s*,\s*[A-Z]+\s*\d{5}(?:-\d{4})?)\b',
        r'which has the address of\s+(\S.*?)\s*;?\s*\n',
        r'Collateral Address: (.+?)\n'
    ]

    # Try each pattern in sequence
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()

    return None  # Return None if no match is found

def extract_owner_details(text):
    # Define a regular expression pattern to match the owner's name
    owner_pattern = re.compile(r'\bvs\.\s+(.+?)\s+\b')

    # Search for the pattern in the text
    owner_match = owner_pattern.search(text)

    # If a match is found, extract the owner's name
    if owner_match:
        owner_name = owner_match.group(1)

        # Split the owner's name into first name and last name
        name_parts = owner_name.split()
        first_name = name_parts[0] if name_parts else None
        last_name = name_parts[-1] if name_parts else None

        # Create a dictionary with the extracted information
        owner_details = {
            "first_name": first_name,
            "last_name": last_name
        }

        return owner_details
    else:
        return None  # Return None if no match is found

def extract_mailing_address(text):
    # Define a regular expression pattern to match the mailing address after "vs"
    pattern = re.compile(r'\bvs\b[^\n]*\n(.+?)\n(?:-AND\b|$)', re.IGNORECASE | re.DOTALL)

    # Search for the pattern in the text
    match = pattern.search(text)

    # If a match is found, extract the mailing address
    if match:
        mailing_address = match.group(1).strip()
        return mailing_address
    else:
        return None  # Return None if no match is found

def process_pdf(pdf_path):
    # Extract text from the PDF
    extracted_text = extract_text_from_pdf(pdf_path)

    # Extract property address from the extracted text
    property_address = extract_property_address(extracted_text)

    # Extract owner details from the extracted text
    owner_details = extract_owner_details(extracted_text)

    # Extract mailing address from the extracted text
    mailing_address = extract_mailing_address(extracted_text)

    # Print the results for each PDF
    print(f"\nProcessing PDF: {pdf_path}")

    output_dict = {
        "Property Address": property_address,
        # "Owner Details": owner_details,
        # "Mailing Address": mailing_address
    }

    print(json.dumps(output_dict, indent=2))

def process_folder(folder_path):
    # Get a list of PDF files in the specified folder
    pdf_files = [file for file in os.listdir(folder_path) if file.lower().endswith('.pdf')]

    # Process each PDF file in the folder
    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        process_pdf(pdf_path)

if __name__ == "__main__":
    # Specify the folder path containing the PDF files
    folder_path = r'C:\Users\hls\Downloads\Testing_County_pdfs'

    # Process the folder and print the results
    process_folder(folder_path)
