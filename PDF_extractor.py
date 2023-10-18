import PyPDF2
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

# Set the path to the Tesseract executable (update this with your path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)  # Use PdfReader instead of PdfFileReader

        text = ''
        # Loop through each page in the PDF
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]

            # Convert the PDF page to images
            images = convert_from_path(pdf_path, first_page=page_num + 1, last_page=page_num + 1)

            # Extract text from each image using OCR
            for image in images:
                text += pytesseract.image_to_string(image)

    return text

pdf_path = r'C:\Users\hls\Downloads\County1.pdf'
extracted_text = extract_text_from_pdf(pdf_path)
print(extracted_text)
