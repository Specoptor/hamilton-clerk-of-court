import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re


# Set the path to the Tesseract executable (update this with your path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path):
    try:
        # Open the image file
        with Image.open(image_path) as img:
            # Apply pre-processing techniques
            img = img.convert('L')  # Convert to grayscale
            img = img.filter(ImageFilter.MedianFilter())  # Apply median filter
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2)  # Increase contrast

            # Use Tesseract to do OCR on the pre-processed image
            text = pytesseract.image_to_string(img)
            return text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return None


def extract_movie_title(text):
    # Regex pattern to capture the movie title
    pattern = r'(Paul Giamatti S a\s*?Mr\. Hunham\.)'

    # Search for the pattern in the text
    match = re.search(pattern, text)

    # Return the captured group if found, otherwise return None
    return match.group(1) if match else None


def extract_movie_date(text):
    # Regex pattern to capture the movie date
    pattern = r'(\bJanuary|\bFebruary|\bMarch|\bApril|\bMay|\bJune|\bJuly|\bAugust|\bSeptember|\bOctober|\bNovember|\bDecember)\s+(\d{1,2})'

    # Search for the pattern in the text
    match = re.search(pattern, text)

    # Return the captured group if found, otherwise return None
    return f"{match.group(1)} {match.group(2)}" if match else None


def extract_movie_summary(text):
    # Regex pattern to capture the movie summary
    pattern = r'(Paul Giamatti stars in .*? everywhere November)'

    # Search for the pattern in the text
    match = re.search(pattern, text, re.DOTALL)  # re.DOTALL to match newlines

    # Return the cleaned summary if found, otherwise return None
    if match:
        summary = match.group(1)
        # Remove unwanted symbols
        cleaned_summary = re.sub(r'[^a-zA-Z\d\s,]', '', summary)
        return cleaned_summary.strip()
    else:
        return None


# Extracting the movie summary from the sample text


if __name__ == "__main__":
    # Specify the path to the image file
    image_path = r'C:Users\hls\Downloads\AI_pic.png'

    # Extract text from the image
    extracted_text = extract_text_from_image(image_path)

    if extracted_text:
        # print("Extracted Text:")
        print(extracted_text)
    else:
        print("Text extraction failed.")

    movie_title = extract_movie_title(extracted_text)
    print("Movie Title : ",movie_title)

    movie_date = extract_movie_date(extracted_text)
    print("Date :",movie_date)

    movie_summary = extract_movie_summary(extracted_text)
    print("Summary :", movie_summary)