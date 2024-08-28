import csv
from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

# Set this to False to include all rows
# Set this to True to only include rows with "Today" in the "Date Published" column
FILTER_TODAY = True

def setup_driver():
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service)

def scrape_trades(driver, url, filter_today=False):
    # Get today's date in the desired format
    today_date = datetime.now().strftime("%Y %b %d")

    driver.get(url)
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr.q-tr')))
    trade_rows = driver.find_elements(By.CSS_SELECTOR, 'tr.q-tr')
    data = []
    for row in trade_rows:
        row_data = []
        try:
            cells = row.find_elements(By.CSS_SELECTOR, 'td.q-td')
        except StaleElementReferenceException:
            # Reacquire the reference to row or add a wait
            row = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.YOUR_ROW_IDENTIFIER, "your row identifier value"))
            )
            cells = row.find_elements(By.CSS_SELECTOR, 'td.q-td')
        if len(cells) < 8:  # Ensure there are enough cells in the row
            continue

        for index, cell in enumerate(cells):
            if index in [5]:  # Skip "Owner"
                continue

            cell_text = cell.text.strip().replace('\n', ' ')
            if index == 0:  # Politician's name cell
                cell_text_parts = cell_text.split()
                cell_text = ' '.join(cell_text_parts[:-1])  # Exclude party and state
            elif index == 2 and 'Today' in cell_text:  # Replace 'Today' with the actual date
                cell_text = cell_text.replace('Today', today_date)

            row_data.append(cell_text)

        if filter_today and today_date not in row_data[2]:  # Check "Date Published" for today's date
            continue

        data.append(row_data)
    return data


def write_to_csv(data, filename):
    # Check if the file already exists and has content
    file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0

    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # If the file doesn't exist or is empty, write the header
        if not file_exists:
            header = ["Politician", "Issuer", "Date Published", "Transaction Date", "Reporting Gap", "Trade Type", "Trade Size", "Trade Price"]
            writer.writerow(header)
            print(' | '.join(header))  # Print the header

        for row in data:
            writer.writerow(row)
            print(' | '.join(row))

def main():
    url = '''
    https://www.capitoltrades.com/trades?txType=buy&txType=sell&assetType=etf&assetType=etn&assetType=indices&assetType=stock&per_page=48    '''
    driver = setup_driver()
    try:
        trades_data = scrape_trades(driver, url, FILTER_TODAY)
        write_to_csv(trades_data, 'trades_data.csv')
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
