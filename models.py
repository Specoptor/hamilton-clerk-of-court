# misc imports
import time

# selenium imports
from selenium import webdriver
from selenium.common import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# local imports
import xpaths
from utils import wait_for_pdf_download, pdf_downloaded_successfully, attempt_to_download_again


class TableReader:
    """
    A class to read table data from the webpage.
    """

    def __init__(self, drv: webdriver.Chrome):
        """
        Constructor.

        :param drv: the webdriver instance.
        """
        self.drv = drv
        self.table_data = self._read_table()

    def _read_table(self, table_xpath: str='//*[@id="cpciv_classification_results"]/tbody') -> list[dict[str, str]]:
        """
        Read the table data from the webpage and populate the table_data list.

        1. Find the table body element
        2. Get all rows in the table body element
        3. For each row, get all the td elements
        4. For each td element, get the text content. Here is the mapping:
            td[0] -> case number
            td[1] -> date filed
            td[2] -> caption
            td[3] -> class

        :return: a list of dict, each dict contains the data for a row.
        """

        # find the table element
        table_element = self.drv.find_element(By.XPATH, table_xpath)
        # find all rows in the table element
        rows = table_element.find_elements(By.TAG_NAME, "tr")
        results = []  # output
        for row_element in rows:
            row_data = {}
            td_elements = row_element.find_elements(By.TAG_NAME, "td")
            row_data['case_number'] = td_elements[0].text  # first column
            row_data['date_filed'] = td_elements[1].text  # second column
            row_data['caption'] = td_elements[2].get_attribute('textContent')  # third column
            row_data['class'] = td_elements[3].text  # fourth column
            results.append(row_data)

        return results


class DocumentProcessor:

    def __init__(self, driver: webdriver.Chrome, table_reader: TableReader):
        self.driver = driver
        self.table_reader = table_reader

    def save_all_initial_filing_docs(self) -> None:
        """
        save all the initial filing docs

        1. Loop through the table data
        2. Open the case docs webpage using the case number to open that specific case
        3. Find the initial filing row in the case docs table
        4. Click the button to download the PDF
        5. Wait for the file to download to complete
        6a. If the file is not downloaded successfully, attempt again a few times
        6b. Close the case docs tab
        7. Move to the main window
        8. Refresh the main window
        9. Show all rows
        10. Continue with the loop

        :return:
        """

        def _find_initial_filling_row(_case_docs_table: WebElement) -> WebElement:
            """
            Find the initial filing row in the case docs table.

            :param _case_docs_table: The case docs table.
            :return: The initial filing row.
            """
            rows = _case_docs_table.find_elements(By.TAG_NAME, "tr")
            for _row in rows[1:]:  # skip the header row
                # all td elements in the current row
                row_data_elements = _row.find_elements(By.TAG_NAME, "td")
                # the second column contains the doc type
                if row_data_elements[1].text == 'Initial Filing':
                    # the fifth column is the button to open the initial doc
                    initial_filing_doc_button = row_data_elements[4]
                    return initial_filing_doc_button

            else:
                raise Exception("Initial filing row not found.")

        for ctr, row in enumerate(
                self.table_reader.table_data):  # row contains case number needed to click the case doc buttons

            # Open case docs tab
            case_number = row['case_number'].replace(' ', '')
            case_doc_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpaths.xpath_to_case_docs_button(case_number))))
            try:
                case_doc_button.click()
            except ElementClickInterceptedException:
                # sometimes the case doc button is not clickable, so we need to wait a bit and try again
                try:
                    # scroll over the case_doc_button for current row
                    self.driver.execute_script("arguments[0].scrollIntoView();", case_doc_button)
                    case_doc_button.click()
                except ElementClickInterceptedException:
                    # click the button using javascript
                    self.driver.execute_script("arguments[0].scrollIntoView();", case_doc_button)

            # Switch to the case docs tab
            self.driver.switch_to.window(self.driver.window_handles[-1])

            # show all rows of case docs
            self.driver.find_element(By.XPATH, xpaths.SHOW_ALL_ROWS_CASE_DOCS).click()

            # find the case docs table
            case_docs_table = self.driver.find_element(By.ID, xpaths.CASE_DOCS_TABLE_ID)

            # find the initial filing row
            initial_filing_row = _find_initial_filling_row(case_docs_table)

            # button to download the PDF.
            initial_filing_doc_button = initial_filing_row.find_element(By.NAME, "submit")

            # click should commence the download the PDF.
            initial_filing_doc_button.click()

            # wait for file to appear in initial_docs directory
            # it takes a few seconds to appear over slow networks
            time.sleep(3)

            # wait for the download to complete
            wait_for_pdf_download()

            if not pdf_downloaded_successfully(case_number):
                attempt_to_download_again(initial_filing_doc_button, case_number)

            # close the case docs tab
            self.driver.close()

            # move to the main window
            self.driver.switch_to.window(self.driver.window_handles[0])

            # refresh the main window
            self.driver.refresh()

            # show all rows
            self.driver.find_element(By.XPATH, xpaths.SHOW_ALL_ROWS_MAIN_TABLE).click()
            # continue with the loop
