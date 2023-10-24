Readme file of dataPDF branch

## About PDF-extractor2.py file
-It extracts the data from PDF
- You need following steps to run file :
## OCR tesseract software 
- download tesseract software from the following link: https://github.com/UB-Mannheim/tesseract/wiki
- Set the path to the Tesseract executable (update this with your path)  like this:
- pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

## Install Poppler:
- You have to download and extract poppler then add the 'bin' folder in poppler directory in System PATH variables.
- After setting up poppler restart the IDE.
- then the file will run.

## About PDF_extractor.py file
- This file uses PYpdf2 library to extract PDF data.
- Not cleaned as compared to pymuPDF.

