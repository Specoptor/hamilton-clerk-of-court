# Foreclosure Records Scraper

This script uses Selenium to automate the process of searching foreclosure records for a given date range on the website `https://www.courtclerk.org/records-search/foreclosure/`. After fetching the records, it prints the count of the results and then leverages the `TableReader` class from `models.py` to extract and print the table data.

### Dependencies

- `selenium`
  
You can install the required dependencies using pip:

```
pip install selenium
```

### Requirements

- Google Chrome browser installed.
- ChromeDriver executable matching the version of the Google Chrome browser. Ensure that the ChromeDriver executable is in the system's `PATH` or in the same directory as the script.

### Usage

1. Navigate to the directory containing `main.py` and `models.py`.
2. Run the main script using:

```
python main.py
```

### Script Walkthrough

1. The script initializes a Chrome web driver and navigates to the BASE_ENDPOINT.
2. Waits implicitly for 10 seconds to ensure the webpage loads completely.
3. Fills the foreclosure search form:
    - Selects a foreclosure category from a dropdown.
    - Enters a begin date (in this example, "08/01/2023").
    - Enters an end date (in this example, "08/31/2023").
    - Clicks the search button.
4. Once the results are loaded, it clicks the "show all rows" button.
5. Retrieves the number of results found and prints it.
6. Uses the `TableReader` class from `models.py` to extract data from the table on the webpage.
7. Prints the table data.

### About `models.py`

- `models.py` contains a class called `TableReader` that is designed to extract table data from a webpage using Selenium.
- The `TableReader` class takes a webdriver instance as a parameter and reads the table data from the given webpage.
- The main functionality is encapsulated in the `_read_table` method, which returns a list of dictionaries, each representing a row from the table.

### Notes

- Ensure that you have a stable internet connection.
- If the structure of the webpage changes, the script may not work as expected. Ensure that the XPATHs and IDs used in the script match the current structure of the website.
- Always make sure to use web scraping responsibly and ethically, and comply with the website's `robots.txt` file or terms of service.

### License

This script and module are provided "as is" without any warranty. Use at your own risk. 

---
