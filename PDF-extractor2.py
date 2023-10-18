import re
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract

# Set the path to the Tesseract executable (update this with your path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_pdf(pdf_path):
    text = ''
    # Open the PDF file using PyMuPDF
    with fitz.open(pdf_path) as pdf_document:
        num_pages = pdf_document.page_count

        # Loop through each page in the PDF
        for page_num in range(num_pages):
            page = pdf_document[page_num]

            # Convert the PDF page to images
            images = convert_from_path(pdf_path, first_page=page_num + 1, last_page=page_num + 1)

            # Extract text from each image using OCR
            for image in images:
                text += pytesseract.image_to_string(image)

    return text

def extract_property_address(text):
    # Define a regular expression pattern to match the property address
    pattern = re.compile(r'PROPERTY ADDRESS: (.+?)\n', re.IGNORECASE)

    # Search for the pattern in the text
    match = pattern.search(text)

    # If a match is found, extract the property address
    if match:
        property_address = match.group(1)
        return property_address
    else:
        return None  # Return None if no match is found

# PDF path
pdf_path = r'C:\Users\hls\Downloads\County1.pdf'

# Extract text from the PDF
extracted_text = extract_text_from_pdf(pdf_path)

# Extract property address from the extracted text
property_address = extract_property_address(extracted_text)

# Print the results
print("Extracted Text:")
print(extracted_text)

print("\nExtracted Property Address:")
if property_address:
    print(f"Property Address: {property_address}")
else:
    print("Property address not found.")
