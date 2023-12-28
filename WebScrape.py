import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

def setup_driver():
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service)

def scrape_trades(driver, url):
    driver.get(url)
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr.q-tr')))
    trade_rows = driver.find_elements(By.CSS_SELECTOR, 'tr.q-tr')
    data = []
    for row in trade_rows:
        row_data = []
        cells = row.find_elements(By.CSS_SELECTOR, 'td.q-td')
        for index, cell in enumerate(cells):
            if index == 5:  # Skip the "Transaction Type" column
                continue
            try:
                cell_text = cell.text.strip().replace('\n', ' ')
                if index == 0:  # Politician's name cell
                    cell_text_parts = cell_text.split()
                    cell_text = ' '.join(cell_text_parts[:-1])
                row_data.append(cell_text)
            except NoSuchElementException:
                row_data.append('Data not found')
        data.append(row_data)
    return data

def write_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        header = ["Politician", "Issuer", "Date Published", "Transaction Date", "Reporting Gap", "Trade Size", "Trade Price", "Transaction ID"]
        writer.writerow(header)
        print(' | '.join(header))  # Print the header
        for row in data:
            writer.writerow(row)
            print(' | '.join(row))

def main():
    url = '''
    https://www.capitoltrades.com/trades?txDate=30d&txType=buy&txType=sell&assetType=etf&assetType=etn&assetType=reit&assetType=stock&assetType=corporate-bond&assetType=municipal-security&per_page=48
    
    '''
    driver = setup_driver()
    try:
        trades_data = scrape_trades(driver, url)
        write_to_csv(trades_data, 'trades_data.csv')
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
