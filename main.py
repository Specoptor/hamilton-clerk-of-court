import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from models import TableReader, DocumentProcessor
from utils import initial_docs_directory

BASE_ENDPOINT = "https://www.courtclerk.org/records-search/foreclosure/"

########### Chrome Options #########
options = webdriver.ChromeOptions()
settings = {
    "download.default_directory": initial_docs_directory(),  # Set default download directory
    "download.prompt_for_download": False,  # Disable prompt
    "download.directory_upgrade": True,  # Enable directory upgrade
    "plugins.always_open_pdf_externally": True  # Disable PDF viewer and always download
}

# add settings to chrome options
options.add_experimental_option("prefs", settings)

# create the webdriver instance
driver = webdriver.Chrome(options=options)

# open the webpage
driver.get(BASE_ENDPOINT)

# ensure the webpage is completely loaded before proceed to fill the form.
driver.implicitly_wait(10)

########### FILL THE FORM ############

# select foreclosure category from dropdown
drop_down_element = Select(driver.find_element(By.XPATH, '//*[@id="cc_frm"]/select'))
drop_down_element.select_by_index(1)

# enter the begin date (mm/dd/yyyy)
begin_date = "08/01/2023"
begin_date_element = driver.find_element(By.ID, "FFC")
begin_date_element.send_keys(begin_date)

# enter the end data (mm/dd/yyyy)
end_date = "08/31/2023"
end_date_element = driver.find_element(By.ID, "date")
end_date_element.send_keys(end_date)

# click the search button
driver.find_element(By.XPATH, '//*[@id="cc_frm"]/input[5]').click()

########### Wait until the results table is loaded ############

# click the show all rows button
show_all_rows_button = driver.find_element(By.XPATH, '/html/body/div[1]/button')
show_all_rows_button.click()

# get the number of results found
number_of_results_tag = driver.find_element(By.XPATH, '/html/body/div[1]/table[1]/tbody/tr[3]/td[2]')
results_count = number_of_results_tag.get_attribute('innerHTML')

# print results count
print(f'results found: {results_count}')

# read the table data
table_reader = TableReader(driver)
table_data = table_reader.table_data
pprint.pprint(table_data)

doc_processor = DocumentProcessor(driver, table_reader)
doc_processor.save_all_initial_filing_docs()
