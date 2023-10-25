import json
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
import pytesseract
from pdf2image import convert_from_path


def resume_paused_downloads(driver: webdriver.Chrome) -> bool:
    """
    Opens the Chrome's downloads in a new tab and clicks the 'Resume' button if found.

    :param driver: The active Selenium WebDriver instance.
    :returns:True if the 'Resume' button was found and clicked, False otherwise.
    """
    # Open a new tab
    driver.execute_script("window.open('');")

    # Switch to the new tab
    driver.switch_to.window(driver.window_handles[-1])

    # Navigate to Chrome's downloads page
    driver.get("chrome://downloads/")

    # Check for the 'Resume' button inside the Shadow DOM and click it if found
    try:
        # JavaScript to access the 'Resume' button inside the Shadow DOM
        js_script = """
        let root = document.querySelector('cr-button').shadowRoot;
        let resumeBtn = root.querySelector('#pauseOrResume');
        if (resumeBtn) {
            resumeBtn.click();
            return true;
        }
        return false;
        """

        # Execute the JavaScript
        result = driver.execute_script(js_script)

        return result
    except:
        return False
    finally:
        # Close the downloads tab and switch back to previous tab
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])


def initial_docs_directory() -> str:
    """
    Path of the directory containing the initial docs. Function creates the directory
    if it does not already exist.

    :return: Absolute path of directory.
    """

    # Define the directory path
    dir_path = os.path.join(os.getcwd(), 'initial_docs')

    # Check if the directory exists, if not create it
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    return dir_path


def get_pdf_count() -> int:
    """
    Get the number of PDF files in the initial docs directory.

    :return: number of PDF files in the directory.
    """
    dir_path = initial_docs_directory()

    # List all PDF files in the directory
    pdf_files = [f for f in os.listdir(dir_path) if f.endswith('.pdf')]

    return len(pdf_files)


def wait_for_pdf_download(timeout: int = 60) -> None:
    """
    Waits until no file in directory has '.crdownload' extension while timeout is not exceeded.

    :param timeout: Maximum time (in seconds) to wait for the download to complete.
    :return: None
    """

    download_dir = initial_docs_directory()
    end_time = time.time() + timeout
    while time.time() < end_time:
        downloads_in_process = [f for f in os.listdir(download_dir) if f.endswith('.crdownload')]
        if not downloads_in_process:
            break
    return None


def pdf_downloaded_successfully(case_number: str) -> bool:
    """
    Check if the case doc for the given case number has been downloaded.

    :param case_number: The case number to check.
    :return: True if the case doc has been downloaded, False otherwise.
    """
    dir_path = initial_docs_directory()
    pdf_files = [f for f in os.listdir(dir_path) if f.endswith('.pdf')]
    downloads_in_process = [f for f in os.listdir(dir_path) if f.endswith('.crdownload')]
    for pdf_file in pdf_files:
        if case_number in pdf_file:
            return True
    else:
        for download in downloads_in_process:
            if case_number in download:
                wait_for_pdf_download()
                return pdf_downloaded_successfully(case_number)
    return False


def attempt_to_download_again(element: WebElement, case_number: str) -> bool:
    """
    Clicks the given element and waits for the download to complete. 1 attempt allowed.

    :param case_number: case number of initial file pdf to download
    :param element: The element to click.
    :return: None
    """
    time.sleep(5)
    if pdf_downloaded_successfully(case_number):
        return True
    else:
        time.sleep(5)
        element.click()
        wait_for_pdf_download()
    return False


def extract_text_from_pdf(pdf_path: str) -> list[str]:
    """
    Extract text from the given PDF file.

    :param pdf_path: path to pdf file.
    :return:
    """
    images = convert_from_path(pdf_path, dpi=150)

    # Initialize an empty string to store the OCR results
    pages = []

    # Extract text from each image using OCR
    for image in images:
        pages.append(pytesseract.image_to_string(image))  # this is more performant than using +=

    return pages


def add_poppler_bin_to_path() -> None:
    """
    Add the Poppler binary path to the system path variable.

    :return: None
    """
    # Determine the root directory (directory of the current script)
    root_directory = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to poppler binaries
    poppler_path = os.path.join(root_directory, 'poppler', 'poppler-23.08.0', 'Library', 'bin')

    # Add the poppler path to the system PATH for the current process
    os.environ["PATH"] += os.pathsep + poppler_path


def process_pdf(pdf_path: str) -> list[str]:
    """
    Extract text from the given PDF filepath

    :param pdf_path: path to pdf file.
    :return: parsed pdf content.
    """
    directory_path = initial_docs_directory()
    if pdf_path.endswith(".pdf"):
        pdf_path = os.path.join(directory_path, pdf_path)
        return extract_text_from_pdf(pdf_path)
    else:
        return []


def process_directory(directory_path: str | None = None) -> dict[str, list[str]]:
    """
    Extract text from all PDF files in the given directory.

    :param directory_path:
    :return: dictionary of case number and text
    """
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    add_poppler_bin_to_path()
    directory_path = directory_path or initial_docs_directory()
    texts = {}
    for filename in os.listdir(directory_path):
        texts[filename.split('_')[0]] = process_pdf(filename)

    # save the pdfs to json file if all pdfs processed successfully.
    if len(texts) == len(os.listdir(directory_path)):
        print(f"Successfully processed {len(texts)} PDF files")
        with open('parsed_pdfs.json', 'w') as f:
            json.dump(texts, f, indent=4)
    return texts


def extract_datapoints_from_pdf(pages: list[str]) -> dict[str, str]:
    """
    Extract datapoints from the given PDF file.

    1. Property Address:
    2. Mailing Address: on second text, after the words "Plaintiff -vs-"
    3. Owner First Name:
    4. Owner Last Name
    5. Property Price
    6. Interest Rate

    :param pages: list of text of each text of the pdf.
    :return: a dictionary containing the datapoints.
    """
    pdf_text = '\n'.join(pages)

    def first_owner(text: str = pages[0]) -> str | None:
        """
        Extracts the owner name by assuming the owner name is the first line after the word "VS." on the first text.

        Regex Explanation:

        ^vs\.\n:
        This part matches the string "vs." at the start of a line followed by a newline character.

        (.*?):
        This part captures any characters (non-greedily) on the line following "vs.".

        (?=\n):
        This part is a lookahead assertion that ensures there's a newline character following the captured text,
        but doesn't include it in the match.

        :param text: first page text of the pdf by default
        :return: first owner name if found else None
        """
        pattern = re.compile(r'(?<=VS\.\n)(.*?)(?=\n)', re.MULTILINE | re.IGNORECASE)
        match = pattern.search(text)
        if match:
            return match.group(0)
        return None

    def second_owner(text: str = pages[1]) -> str | None:
        """
        Extract the second owner name from the second page.

        Regex explanation:
            \d{5}(?:-\d{4})?\s*:
            This part matches a 5-digit zipcode optionally followed by a hyphen and a 4-digit extension,
            followed by any amount of whitespace.

            ([\w\s]+?)\s*\n:
            This part captures one or more word characters or spaces (non-greedily),
            followed by any amount of whitespace and a newline character. This should capture the second owner name,
            as it appears on a new line immediately after the zipcode.

        :param text: second page text of the pdf by default
        :return: second owner name if found else None
        """
        pattern = re.compile(r'\d{5}(?:-\d{4})?\s*([\w\s]+?)\s*\n', re.MULTILINE)
        match = pattern.search(text)
        if match:
            return match.group(1)
        return None

    def property_address(text: str = pdf_text) -> str | None:
        """
        Extract the property address from the entire pdf text.

        Regex Explanation:
            \s*:
            This part matches the text "property address:" (case-insensitively due to re.IGNORECASE) followed by
            any amount of whitespace (\s*).

            (.*?\d{5}(?:-\d{4})?):
            This part captures everything from the text following "property address:"
            up to the zipcode.

            .*?:
            This part matches any character (except for a newline) zero or more times,
            but as few times as necessary to satisfy the pattern (non-greedy match).

            \d{5}(?:-\d{4})?:
            This part matches a 5-digit zipcode followed optionally by a hyphen and
            a 4-digit extension.

            The ?: within the parentheses indicates a non-capturing group, so that the ? repetition applies to the
            entire group (-\d{4}), and not just the last digit.

        :param text: defaults to the entire pdf text
        :return: property address if found else None
        """
        pattern = re.compile(r'property address:\s*(.*?\d{5}(?:-\d{4})?)', re.IGNORECASE)
        match = pattern.search(text)
        if match:
            return match.group(1)
        return None

    def mailing_address(text: str = pages[1]) -> str | None:
        """
        Extract the mailing address from the text.

        Regex Explanation:
            —\s*vs-:
            This part of the pattern matches the literal characters '— vs-' in the text, with any amount of whitespace
            (\s*) between the characters.

            [\s\S]*?:
            [\s\S] is a character class that matches any character, including newlines: \s
            matches any whitespace character, and \S matches any non-whitespace character.
            Together, [\s\S] matches any character.

            *?:
            is a non-greedy qualifier that matches 0 or more occurrences of the preceding character class,
            but as few as necessary to allow the rest of the pattern to match. This part of the pattern essentially
            skips over any characters following '— vs-' until it reaches a pattern that looks like a street address.

            \n:
            This part of the pattern matches a newline character, ensuring that the address capture starts at the
            beginning of a new line.

            (\d+\s[\s\S]+?\d{5}(?:-\d{4})?):
            This is the capturing group that matches and captures the mailing address.

            \d+\s:
                \d+ matches one or more digits, which is typical for the street number at the beginning of an address.
                \s matches a single whitespace character following the street number.

            [\s\S]+?:
                [\s\S] matches any character, and +? is a non-greedy qualifier that matches 1 or more occurrences of the
                preceding character class, but as few as necessary to allow the rest of the pattern to match.

            \d{5}(?:-\d{4})?:
                \d{5} matches exactly 5 digits, which is typical for a zipcode.
                (?:-\d{4})? is an optional non-capturing group that matches a hyphen followed by exactly 4 digits,
                which is typical for the 4-digit extension of a 9-digit zipcode. The ? makes this group optional,
                allowing for either 5-digit or 9-digit zipcodes.

        :param text: defaults to the second page.
        :return: mailing address if found else None
        """
        pattern = re.compile(r'—\s*vs-[\s\S]*?\n(\d+\s[\s\S]+?\d{5}(?:-\d{4})?)', re.MULTILINE)
        match = pattern.search(text)
        if match:
            return match.group(1)
        return None

    def property_price(text: str = pdf_text) -> str | None:
        """
        Extract the first price appearing before the interest rate.

        Regex Explanation:
            (\$[\d,]+(?:\.\d{2})?):
            This is the capturing group for the dollar amount.

            \$:
            Matches the dollar sign.

            [\d,]+:
            Matches one or more digits or commas.

            (?:\.\d{2})?:
            Matches the optional decimal part. ?: makes the group non-capturing

            \.\d{2}:
            matches a decimal point followed by exactly two digits

            ?:
            makes the decimal part optional.

            (?=.*?\d+\.\d+%):
            This is a positive lookahead assertion to ensure the dollar amount appears before the interest rate.

            .*?:
            Matches any characters (non-greedy) between the dollar amount and the interest rate.

            \d+\.\d+%:
            Matches the interest rate pattern
            (one or more digits, a decimal point, one or more digits, and a percentage sign).

        :param text: defaults to the entire pdf text
        :return: property price if found else None
        """
        pattern = re.compile(r'(\$[\d,]+(?:\.\d{2})?)(?=.*?\d+\.\d+%)')
        match = pattern.search(text)
        if match:
            return match.group(1)
        return None

    def interest_rate(text: str = pdf_text) -> str | None:
        """
        Extract the interest rate from the entire pdf_text.

        Regex Explanation:
            \b: Asserts a word boundary, ensuring that the match starts at the beginning of a word.
            \d+: Matches one or more digits before the decimal point.
            \.: Matches the decimal point (escaped since . is a special character in regex).
            \d+: Matches one or more digits after the decimal point.
            %: Matches the percentage sign.

        :param text: defaults to the entire pdf text
        :return: interest rate if found else None
        """
        pattern = re.compile(r'\b\d+\.\d+%')
        match = pattern.search(text)

        if match:
            return match.group(0)
        return None

    return {
        'first_owner': first_owner(),
        'second_owner': second_owner(),
        'property_address': property_address(),
        'mailing_address': mailing_address(),
        'property_price': property_price(),
        'interest_rate': interest_rate(),
    }


def get_processed_pdfs() -> dict[str, list[str]]:
    """
    Get the processed pdfs from the json file. If the file does not exist, process the directory and return the
    processed pdfs.

    :return: a dictionary with key as case number and list of pages as key.
    """
    if os.path.exists('parsed_pdfs.json'):
        with open('parsed_pdfs.json', 'r') as f:
            return json.load(f)
    else:
        return process_directory()
