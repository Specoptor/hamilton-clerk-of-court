# Foreclosure Records Scraper

This tool is designed to automate the process of searching and retrieving foreclosure records from a specific website. It utilizes Selenium WebDriver for browser automation and has utilities to handle PDF downloads, among other tasks.

## Project Structure:

### 1. `main.py`
- **Purpose**: Main driver script for the project.
- **Functionalities**:
   - **Chrome Setup**: Configures Chrome options for seamless document downloading, including setting the default download directory and disabling download prompts.
   - **Web Navigation**: Opens the foreclosure search webpage and waits for it to load.
   - **Form Submission**: Fills out the search form on the webpage, selecting categories, and entering date ranges.
   - **Table Data Retrieval**: After submitting the form, the script clicks a button to show all rows of results, retrieves the number of results, and then processes table data using the `TableReader` class.
   - **Document Processing**: Utilizes the `DocumentProcessor` class to save all initial filing documents.

### 2. `models.py`
- **`TableReader` Class**:
   - Reads table data from the webpage.
   - Processes table rows and maps columns to specific fields like case number, date filed, caption, and class.
- **`DocumentProcessor` Class**:
   - Processes documents linked in the table.
   - Downloads initial filing documents for each entry in the table, ensuring successful downloads and attempting retries if necessary.

### 3. `utils.py`
- **Purpose**: Contains utility functions that assist in various tasks.
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
   - **Dynamic XPath Generation**: A function (`xpath_to_case_docs_button`) is provided to generate the XPath for the case docs button based on a case number.

## Setup & Installation:

1. **Dependencies**:
   - Install the required Python packages using:
     ```
     pip install -r requirements.txt
     ```

2. **Browser Setup**:
   - Ensure you have Google Chrome installed.
   - The corresponding ChromeDriver should be available in your system's PATH for Selenium to function correctly.

## Usage:

1. Navigate to the project directory in your terminal or command prompt.
2. Execute the main script to initiate the scraping process:
    ```
    python main.py
    ```