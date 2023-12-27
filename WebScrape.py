import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

# URL to scrape
url = "https://www.capitoltrades.com/trades?txDate=30d&txType=buy&txType=sell&assetType=etf&assetType=etn&assetType=reit&assetType=stock&assetType=corporate-bond&assetType=municipal-security"

# Set up the WebDriver with ChromeDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open a CSV file to write the data
with open('trades_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write the header
    header = ["Politician", "Issuer", "Date Published", "Transaction Date", "Reporting Gap", "Transaction Type", "Trade Size", "Trade Price", "Transaction ID"]
    writer.writerow(header)
    print(' | '.join(header))  # Print the header

    try:
        # Open the URL
        driver.get(url)

        # Wait for the trade rows to load
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr.q-tr')))

        # Find all trade rows on the page
        trade_rows = driver.find_elements(By.CSS_SELECTOR, 'tr.q-tr')

        for row in trade_rows:
            row_data = []

            # Find all cells in the row
            cells = row.find_elements(By.CSS_SELECTOR, 'td.q-td')

            # Iterate over each cell and add its text content to row_data
            for index, cell in enumerate(cells):
                try:
                    cell_text = cell.text.strip().replace('\n', ' ')

                    # For the politician's name cell, split the text and take only the name part
                    if index == 0:
                        cell_text_parts = cell_text.split()
                        cell_text = ' '.join(cell_text_parts[:-1])

                    row_data.append(cell_text)
                except NoSuchElementException:
                    row_data.append('Data not found')
            
            # Write the row data to the CSV file and print it
            writer.writerow(row_data)
            print(' | '.join(row_data))

    finally:
        # Clean up by closing the browser
        driver.quit()
