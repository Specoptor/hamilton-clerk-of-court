# Foreclosure Records Scraper

This tool is designed to automate the process of searching and retrieving foreclosure records from a specific website. It utilizes Selenium WebDriver for browser automation, utilities to handle PDF downloads, and OCR utilities to extract specific information from downloaded documents.

## Project Structure:

### 1. `main.py`
- **Purpose**: Main driver script for the project.
- **Functionalities**:
  - **Chrome Setup**: Configures Chrome options for seamless document downloading.
  - **Web Navigation**: Opens the foreclosure search webpage.
  - **Form Submission**: Fills out the search form on the webpage.
  - **Table Data Retrieval**: Processes table data using the `TableReader` class.
  - **Document Processing**: Utilizes the `DocumentProcessor` class to save all initial filing documents.

### 2. `models.py`
- **`TableReader` Class**: Reads and processes table data from the webpage.
- **`DocumentProcessor` Class**: Downloads initial filing documents for each entry in the table.

### 3. `utils.py`
- **Purpose**: Contains utility functions for various tasks.
- **Key Functions**:
  - **Resume Downloads**: Resumes any paused downloads in Chrome.
  - **Manage Initial Docs Directory**: Returns or creates a directory path for saving initial docs.
  - **PDF Count**: Retrieves the number of PDFs present in the initial docs directory.
  - **Wait for PDF Download**: Pauses the script until a PDF finishes downloading or a timeout is reached.
  - **Check PDF Download**: Checks if a document corresponding to a specific case number has been downloaded successfully.
  - **Retry Download**: If a download fails, this function attempts to download the document again.

### 4. `xpaths.py`
- **Purpose**: Provides XPath constants and a dynamic XPath generation function.
- **Key Functionalities**:
  - **XPath Constants**: Contains predefined XPaths for various elements in the website.
  - **Dynamic XPath Generation**: Generates the XPath for the case docs button based on a case number.

### 5. PDF Text Extraction & Data Point Processing:

#### `extract_text_from_pdf`
- Extracts text from a given PDF file using OCR.

#### `add_poppler_bin_to_path`
- Adds the Poppler binary path to the system path variable. Make sure Poppler is available at the root of the project directory.

#### `process_directory`
- Extracts text from all PDF files in a given directory.

#### `extract_datapoints_from_pdf`
- Extracts specific data points from the OCR results of a PDF file. Data points include:
  - **Property Address**: Extracted based on the regex pattern that looks for the string "property address:" followed by characters leading up to a zip code pattern.
  - **Mailing Address**: Extracted from the second page of the PDF, typically appearing after the string "— vs-".
  - **Owner Names**: The first and second owner names are extracted based on their positions relative to specific markers, such as "VS." and zip code patterns.
  - **Property Price**: Extracted by looking for a dollar amount appearing before an interest rate.
  - **Interest Rate**: Extracted based on its common pattern which includes digits, a decimal point, followed by more digits and a percentage sign.

### 6. `pdf_extractor_playground.py`
- **Purpose**: A module created to experiment with PDF parsing and extraction.
- **Functionalities**:
  - **Process Directory**: Uses the `process_directory` function from `utils` to extract text from PDF files.
  - **Extract Data Points**: For each PDF, it utilizes the `extract_datapoints_from_pdf` function to extract various data points and prints them.

## Setup & Installation:

1. **Dependencies**:
  - Install the required Python packages using:
    ```
    pip install -r requirements.txt
    ```

2. **Browser Setup**:
  - Ensure you have Google Chrome installed.
  - The corresponding ChromeDriver should be available in your system's PATH for Selenium to function correctly.

3. **OCR Setup**:
  - Tesseract OCR should be installed on your machine. The path to the Tesseract executable should be correctly configured in the utility functions.

4. **Poppler Setup**:
  - Poppler, a PDF rendering library, should be available and its binary path should be added to your system's path. This is required for PDF to image conversion, which is a prerequisite for OCR.

## Usage:

1. Navigate to the project directory in your terminal or command prompt.
2. Execute the main script to initiate the scraping process:
    ```bash
    python main.py
    ```
3. Parse the pdf files in the `initial_docs` directory using the `pdf_extractor_playground.py` module:
    ```bash
    python pdf_extractor_playground.py
    ```