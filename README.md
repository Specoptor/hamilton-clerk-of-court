
# README for `main.py`

## Foreclosure Records Scraper

This script uses Selenium to automate the process of searching foreclosure records for a given date range on the website `https://www.courtclerk.org/records-search/foreclosure/`. Once the records are fetched, it will print the count of the results found.

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

1. Navigate to the directory containing `main.py`.
2. Run the script using:

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

### Notes

- Ensure that you have a stable internet connection.
- If the structure of the webpage changes, the script may not work as expected. Ensure that the XPATHs and IDs used in the script match the current structure of the website.
- Always make sure to use web scraping responsibly and ethically, and comply with the website's `robots.txt` file or terms of service.

### License

This script is provided "as is" without any warranty. Use at your own risk. 

---
