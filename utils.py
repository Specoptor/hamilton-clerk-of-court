import os
import time
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement


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
            return
    return None


def pdf_downloaded_successfully(case_number: str) -> bool:
    """
    Check if the case doc for the given case number has been downloaded.

    :param case_number: The case number to check.
    :return: True if the case doc has been downloaded, False otherwise.
    """
    dir_path = initial_docs_directory()
    pdf_files = [f for f in os.listdir(dir_path) if f.endswith('.pdf')]
    formatted_case_number = case_number.replace(' ', '')
    for pdf_file in pdf_files:
        if formatted_case_number in pdf_file:
            return True
    return False


def attempt_to_download_again(element: WebElement, case_number: str) -> bool:
    """
    Clicks the given element and waits for the download to complete.

    :param case_number: case number of initial file pdf to download
    :param element: The element to click.
    :return: None
    """
    element.click()
    wait_for_pdf_download()
    for i in range(5):
        while not pdf_downloaded_successfully(case_number):
            wait_for_pdf_download()
            return True
    return False
