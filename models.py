from selenium import webdriver
from selenium.webdriver.common.by import By


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

    def _read_table(self, table_xpath='//*[@id="cpciv_classification_results"]/tbody') -> list[dict[str, str]]:
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
