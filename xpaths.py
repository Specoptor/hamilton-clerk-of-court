MAIN_TABLE_XPATH = '//*[@id="cpciv_classification_results"]/tbody'
SHOW_ALL_ROWS_CASE_DOCS = '/html/body/div[1]/table/tbody/tr[2]/td/button'
SHOW_ALL_ROWS_MAIN_TABLE = '/html/body/div[1]/button'
CASE_DOCS_TABLE_ID = 'case_docs_table'


def xpath_to_case_docs_button(case_number: str) -> str:
    """
    Return the xpath of the initial filing document button.
    1. format the case number by removing space between 'A' and digits. 
    2. generate the xpath.
    
    :param case_number: Raw string extracted from the main table.
    :return: Xpath to look for in the case docs webpage.
    """
    formatted_case_number = case_number.replace(' ', '')
    return f'//*[@id="{formatted_case_number}_doc"]/input[3]'


