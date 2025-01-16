import csv
import time
import os
import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import re 

def scrape_business_info(business_type, location):
    # Create the output folder if it doesn't exist
    if not os.path.exists('output'):
        os.makedirs('output')

    print(f"Searching for {business_type} in {location}")

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--lang=en-US")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Set up Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open Google Maps
    driver.get('https://www.google.com/maps')

    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'searchboxinput'))
        )
        search_query = f'{business_type} in {location}'
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'hfpxzc'))
        )
    except Exception as e:
        print("Error: Failed to load search results", e)
        driver.quit()
        return

    # Initialize the lists for output
    names, phones, urls = [], [], []
    business_urls = []

    while True:
        try:
            businesses = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'hfpxzc'))
            )
        except:
            break

        time.sleep(2)
        for business in businesses:
            url = business.get_attribute('href')
            if url and url not in business_urls:
                business_urls.append(url)

        driver.execute_script("arguments[0].scrollIntoView();", businesses[-1])
        time.sleep(2)

        try:
            new_businesses = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'hfpxzc'))
            )
            if len(new_businesses) == len(businesses):
                break
        except:
            break

    for url in business_urls:
        driver.get(url)

        try:
            name = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'lfPIob'))
            ).text
        except:
            name = ""

        try:
            business_url = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-item-id*='authority']"))
            ).text
            url_match = re.search(r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', business_url)
            clean_url = url_match.group(0) if url_match else ""
        except:
            business_url = ""

        try:
            phone = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-item-id*='phone:tel:']"))
            ).text
            phone = "".join(re.findall(r'\d+', phone))
        except:
            phone = ""

        names.append(name)
        phones.append(phone)
        urls.append(clean_url)

    driver.quit()

    csv_filename = f'output/{business_type.replace(" ", "_")}_{location.replace(" ", "_")}.csv'

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Phone', 'Url'])
        for name, phone, url in zip(names, phones, urls):
            writer.writerow([name, phone, url])

    return csv_filename
    # print(f'Successfully scraped {len(names)} businesses.')
    # print(f'Data saved to {csv_filename}')

# business_type = "software company" 
# location = "ahmedabad"
# scrape_business_info(business_type, location)
