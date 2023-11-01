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
    pdf_text = ' '.join(pages)

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
            1. First check for the absence of a second owner using the re.search function to look for
            "JOHN DOE", "JANE DOE", or "HEIR" in the text. If any of these strings are found,
            None is returned, indicating no second owner.

            2. If none of these strings are found, the function attempts to extract the second owner's name using the
             re.search function with a regex pattern:

                i. (?:\d{5}(?:-\d{4})?.*\n){1,2}: This part of the pattern attempts to match the address block,
                which may span one or two lines, ending with a newline character \n.

                ii. ([A-Z\s]+)\n\d+: This part of the pattern captures the second owner's name, which is assumed to be
                 uppercase letters possibly separated by spaces, followed by a newline character \n and the beginning
                 of another address block (or parcel number).

        :param text: second page text of the pdf by default
        :return: second owner name if found else None
        """
        # Check for conditions where there is no second owner
        if re.search(r'\b(JOHN DOE|JANE DOE|HEIR|UNKNOWN SPOUSE)\b', text, re.IGNORECASE):
            return None

        # Try to match a common pattern for the second owner's name
        match = re.search(r'(?:\d{5}(?:-\d{4})?.*\n){1,2}([A-Z\s]+)\n\d+', text, re.MULTILINE)
        if match:
            return match.group(1).strip()

        patterns = [
            r'(?<=\d{5}\n\n)(.*?)(?=\n+\d{4,5}\s)',
            r'(?<=and\n)([A-Za-z\s]+)(?=\n\d{4,5}\s)',
            r'(?<=and\n\n)([A-Za-z\s]+)(?=\n\d{4,5}\s)',
            r'(?<=\d{5}\n\n)([\s\S]*?)(?=\n+\d{4,5}\s)'
        ]

        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text)
            if match:
                checks = ['also serve at:','united states', 'plaintiff', 'in the court of common']
                for check in checks:
                    if not match.group(1).lower().startswith(check):
                        continue
                    else:
                        break
                else:
                    return match.group(1).strip()

        return None

    def property_address(text: str = pdf_text) -> str | None:
        """
        Extract the property address from the entire pdf text.

        Regex Explanation:
            - General:
                \s*:
                This part matches any amount of whitespace (\s*).

            - Pattern1:
                property address:\s*(.*?\d{5}(?:-\d{4})?):
                This pattern is designed to capture the text following "property address:" up to the zipcode.

                .*?:
                This part matches any character (except for a newline) zero or more times,
                but as few times as necessary to satisfy the pattern (non-greedy match).

                \d{5}(?:-\d{4})?:
                This part matches a 5-digit zipcode followed optionally by a hyphen and
                a 4-digit extension.

                The ?: within the parentheses indicates a non-capturing group, so that the ? repetition applies to the
                entire group (-\d{4}), and not just the last digit.

            - Pattern2:
                Property Address:\s*((?:.|\n)+?)(?=\n\n|\Z|\n[a-zA-Z]):
                This pattern is designed to capture the text following "Property Address:" up to either two newline characters,
                the end of the text, or a newline followed by a letter.

                (?:.|\n)+?:
                This part matches any character or newline, one or more times, but as few times as necessary to
                satisfy the pattern (non-greedy match). The ?: indicates a non-capturing group.

                (?=\n\n|\Z|\n[a-zA-Z]):
                This is a positive lookahead assertion. It requires the text following the captured group to either be
                two newline characters, the end of the text (\Z), or a newline followed by a letter, without including
                this text in the captured group.

        :param text: defaults to the entire pdf text
        :return: property address if found else None
        """
        # Split the text by the '[Property Address]' marker
        parts = text.split('[Property Address]')
        if len(parts) >= 2:
            # Get the portion of text before the '[Property Address]' marker
            preceding_text = parts[0].strip()
            # Split the preceding text into lines and reverse the order so we examine lines from bottom to top
            lines = preceding_text.split('\n')[::-1]
            # Initialize an empty string to hold the address
            address = ''
            # Iterate over up to the first 3 lines preceding the marker, stopping when a zipcode is found
            for i, line in enumerate(lines[:3]):
                # Prepend the current line to the address string
                address = line.strip() + ', ' + address if address else line.strip()
                # If a zipcode pattern is found in the address, return the address
                if re.search(r'\d{5}(?:-\d{4})?$', address):
                    if address.startswith("Cincinnati, OH"):
                        # append the preceding line
                        address = lines[i + 1].strip() + ', ' + address
                    return address

        pattern1 = re.compile(r'property address:\s*(.*?\d{5}(?:-\d{4})?)', re.IGNORECASE)
        match1 = pattern1.search(text)
        if match1 and not match1.group(1).startswith("1. BORROWER'S"):
            address = match1.group(1)
            return address

        pattern2 = re.compile(r'Property Address:\s*((?:.|\n)+?)(?=\n\n|\Z|\n[a-zA-Z])', re.IGNORECASE | re.DOTALL)
        match2 = pattern2.search(text)
        if match2:
            address = match2.group(1).strip().replace('\n', ', ')
            address = re.sub(r'\s+', ' ', address).strip()
            return address

        return None

    def mailing_address(text: str = pages[1]) -> str | None:
        """
        Extract the mailing address from the text.

        :param text: defaults to the second page.
        :return: mailing address if found else None
        """
        # Define the regular expressions
        pattern_1 = re.compile(r'[A-Z\s]+\n((?:\d+.*\n)+[A-Z\s]+,\s+[A-Z]+\s+\d{5}(?:-\d{4})?)', re.MULTILINE)
        pattern_2 = re.compile(
            r'(?i:Plaintiff).*?(?:\b\d{3}-\d{4}-\d{4}-\d{2}\b|PARCEL NUMBER:.*?\n|Parcel No\..*?\n)?(\d+.*?\d{5})',
            re.MULTILINE | re.DOTALL)
        parcel_no_pattern = re.compile(r'(Parcel No\. |Parcel No: |PPN# )\d{3}-\d{4}-\d{4}-\d{2}')
        standalone_parcel_pattern = re.compile(r'\d{3}-\d{4}-\d{4}-\d{2}')

        # Try to find a match using pattern_1
        match_1 = pattern_1.search(text)
        if match_1:
            address = match_1.group(1).strip()
            address = parcel_no_pattern.sub('', address)  # Remove all parcel number formats
            address = standalone_parcel_pattern.sub('', address)  # Remove the standalone "248-0001-0142-00" pattern
            if "Address Unknown" in address:  # Check for the unwanted string
                return None
            return address

        # Try to find a match using pattern_2
        match_2 = pattern_2.search(text)
        if match_2:
            address = match_2.group(1).strip()
            address = parcel_no_pattern.sub('', address)  # Remove all parcel number formats
            address = standalone_parcel_pattern.sub('', address)  # Remove the standalone "248-0001-0142-00" pattern

            # Check for specific redundant patterns and skip them
            redundant_patterns = [
                "1. Plaintiff, Harvey Point",
                "2. There has been a default",
                "04920115-1 E-FILED",
                "593-0005-0175-00\n\n-VS-\n\nUnknown heirs,"
            ]
            if any(pattern.lower() in address.lower() for pattern in
                   redundant_patterns) or "Address Unknown" in address:
                return None

            return address

        return None
    def property_price(text: str = pdf_text) -> str | None:
        """
        Extract the first price appearing before the interest rate, or the dollar amount
        immediately following "LOAN AMOUNT" or "Principal Amount" or "original amount"
        if the previous patterns didn't find a match.

        Regex Explanation:
            Interest Rate Match:
                (\$[\d,]+(?:\.\d{2})?)(?=.*?\d+\.\d+%):
                This pattern looks for a dollar amount followed by an interest rate.

                \$:
                Matches the dollar sign symbol.

                [\d,]+:
                Matches one or more digits or commas.

                (?:\.\d{2})?:
                This is a non-capturing group that matches a decimal point followed by two digits, made optional by the trailing ?.

                (?=.*?\d+\.\d+%):
                This is a positive lookahead assertion that ensures the dollar amount is followed by an interest rate,
                without including the interest rate in the match.

                .*?:
                This part matches any character (except for a newline) zero or more times,
                but as few times as possible to satisfy the pattern (non-greedy match).

                \d+\.\d+%:
                This part matches the interest rate pattern: one or more digits, a decimal point, one or more digits,
                and a percentage sign.

            New Pattern 1:
                LOAN AMOUNT\s*:\s*(\$[\d,]+(?:\.\d{2})?):
                This pattern looks for the phrase "LOAN AMOUNT" followed by a dollar amount.

                LOAN AMOUNT\s*:\s*:
                Matches the phrase "LOAN AMOUNT" followed by any amount of whitespace, a colon,
                and any amount of whitespace.

                (\$[\d,]+(?:\.\d{2})?):
                This is the capturing group for the dollar amount, with the same structure as
                in the initial pattern.

            New Pattern 2:
                Principal Amount\s*:\s*(\$[\d,]+(?:\.\d{2})?):
                This pattern looks for the phrase "Principal Amount" followed by a dollar amount.

                Principal Amount\s*:\s*:
                Matches the phrase "Principal Amount" followed by any amount of whitespace, a colon,
                and any amount of whitespace.

                (\$[\d,]+(?:\.\d{2})?):
                This is the capturing group for the dollar amount, with the same structure as
                in the initial and new pattern 1.

            New Pattern 3:
                (?i:original amount).*?(\$[\d,]+(?:\.\d{2})?):
                This pattern looks for the phrase "original amount" (case-insensitive) followed by a dollar amount.

                (?i:original amount).*?:
                Matches the phrase "original amount" followed by any characters (non-greedy) up to the dollar amount.

                (\$[\d,]+(?:\.\d{2})?):
                This is the capturing group for the dollar amount, with the same structure as in the initial pattern and new patterns 1 and 2.

        :param text: defaults to the entire pdf text
        :return: property price if found else None
        """

        # def find_largest_dollar_amount(text: str) -> str | None:
        #     """
        #     Find the largest dollar amount in the given text.
        #
        #     :param text: content to search in
        #     :return: text format of the dollar amount
        #     """
        #     # Step 1: Use regex to find all dollar amounts
        #     pattern = re.compile(r'\$([\d,]+(?:\.\d{2})?)')
        #     amounts = pattern.findall(text)
        #
        #     # Step 2: Convert strings to float numbers
        #     comma_less_amounts = [amount.replace(',', '') for amount in amounts if amount]
        #     float_amounts = [float(amount.replace(',', '')) for amount in comma_less_amounts
        #                      if amount]
        #     float_amounts = [amount for amount in float_amounts if 10000 < amount < 1000000]
        #
        #     if not float_amounts:
        #         return None  # Return None if no dollar amounts were found
        #
        #     # Step 3: Find the largest number
        #     largest_amount = max(float_amounts)
        #
        #     # Step 4: Convert the largest number back to a string with the desired format
        #     largest_amount_str = f"${largest_amount:,.2f}"
        #     return largest_amount_str
        #
        # amount = find_largest_dollar_amount(text)
        # if amount:
        #     return amount

        # New pattern to match "LOAN AMOUNT" followed by a dollar amount
        new_pattern1 = re.compile(r'(?i:LOAN\s*(?:AMOUNT)?)\s*:\s*(\$[\d,]+(?:\.\d{2})?)')
        new_match1 = new_pattern1.search(text)
        if new_match1:
            return new_match1.group(1)

        # Additional pattern to match "Principal Amount" followed by a dollar amount
        new_pattern2 = re.compile(r'(?i:Principal\s*(?:AMOUNT)?)\s*:\s*(\$[\d,]+(?:\.\d{2})?)')
        new_match2 = new_pattern2.search(text)
        if new_match2:
            return new_match2.group(1)

        preceding_interest_rate_pattern = re.compile(r'(\$[\d,]+(?:\.\d{2})?)(?=.*?\d+\.\d+%)')
        preceding_interest_rate_match = preceding_interest_rate_pattern.search(text)
        if preceding_interest_rate_match:
            return preceding_interest_rate_match.group(1)

        # Extract the first dollar amount appearing after the original amount
        new_pattern3 = re.compile(r'(?i:original\s*(?:AMOUNT)?)\s*.*?(\$[\d,]+(?:\.\d{2})?)')
        new_match3 = new_pattern3.search(text)
        if new_match3:
            return new_match3.group(1)

        pattern4 = re.compile(r'(?i:promise to pay).*?(\$[\d,]+(?:\.\d{2})?)')
        match4 = pattern4.search(pdf_text)
        if match4:
            return match4.group(1)

        return None

    def extract_hoa_amount(text: str = pdf_text) -> str | None:
        """
            Extract the HOA amount from the text based on the given pattern.

            :param text: The text from which to extract the HOA amount.
            :return: The extracted HOA amount if found, else None.
            """
        # Define the regular expression for the HOA amount pattern
        # This regex focuses on the phrase structure and the amount format, allowing for variations in the person's name and written-out amount.
        hoa_pattern = re.compile(r'owes the Association the sum of .*?\(\$(\d{1,3}(?:,\d{3})*\.\d{2})\)')

        # Search for the pattern in the text
        match_hoa = re.search(hoa_pattern, text)

        # If a match is found, return the matched HOA amount; otherwise return None
        if match_hoa:
            return match_hoa.group(0)

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

        pattern_2 = r"interest\s+\D*\s*(\d+%)"
        # Using the updated regex to find the percentage value in the sample text
        match_2 = re.search(pattern_2, text)
        # Extracting the matched percentage (including % sign) if
        if match_2:
            return match_2.group(1)

        match_mixed_case = re.search(r"(?i)Principal\s+has\s+been\s+paid[^\d]*(\d{1,2}\.\d+)\s*%", text)
        match_value_mixed_case = match_mixed_case.group(1) if match_mixed_case else None
        return match_value_mixed_case



    return {
        'first_owner': first_owner(),
        'second_owner': second_owner(),
        'property_address': property_address(),
        'mailing_address': mailing_address(),
        'property_price': property_price(),
        'interest_rate': interest_rate(),
        'HOA Amount' : extract_hoa_amount(),
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