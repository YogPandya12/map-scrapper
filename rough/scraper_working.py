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

# Create the output folder if it doesn't exist
if not os.path.exists('output'):
    os.makedirs('output')

parser = argparse.ArgumentParser(description='Scrape businesses from Google Maps')
parser.add_argument('--business_type' , '-bt', '-business_type','--bt', type=str, nargs="+")
parser.add_argument('--location', '-l', '-location', '--l', type=str, nargs="+")

args = parser.parse_args()

location_args = args.location
location = " ".join(location_args)

business_type_args = args.business_type
business_type = " ".join(business_type_args)

print(f"Searching for {business_type} in {location}")


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

# Initialize Chrome driver
# driver = webdriver.Chrome()

# Open the website
driver.get('https://www.google.com/maps')

# Wait for the search box to load
try:
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'searchboxinput'))
    )

    # Type the search query and press Enter
    search_query = f'{business_type} en {location}'
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)

    # Wait for the search results to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'hfpxzc'))
    )
except:
    # If an exception occurs, retry the code block after a short delay
    time.sleep(5)
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
    except:
        # If the problem persists, print an error message and exit the script
        print("Error: Failed to load search results")
        driver.quit()
        exit()

# Google maps and results are successfully loaded    
# Initialize the output list
output = []
urls = []

while True:
    try:
        # Find all the businesses in the search results
        businesses = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'hfpxzc'))
        )
    except:
        # If no businesses are found, break the loop
        break

    time.sleep(2)

    # Store the URLs of the businesses
    for business in businesses:
        url = business.get_attribute('href')
        if url not in urls:
            urls.append(url)

    # Scroll down to load more businesses
    driver.execute_script("arguments[0].scrollIntoView();", businesses[-1])
    time.sleep(2)

    try:
        # Check if new businesses are loaded
        new_businesses = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'hfpxzc'))
        )
        if len(new_businesses) == len(businesses):
            # If no new businesses are loaded, break the loop
            break
    except:
        # If an exception occurs, break the loop
        break


# Visit each business URL and scrape the data
for url in urls:
    driver.get(url)

    try:
        name = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'lfPIob'))
        ).text
    except Exception as e:
        name = ""

    try:
        url = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-item-id*='authority']"))
        ).text
    except Exception as e:
        url = ""

    try:
        phone = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-item-id*='phone:tel:']"))
        ).text
    except Exception as e:
        phone = ""
        
    if name and phone and url:
        print(name, phone, url)
        output.append((name, phone, url))
    elif name and phone:
        output.append((name, phone))
    elif name and url:
        print(name, url)
        output.append((name, url))
    else:
        print("no name or phone found for: ", name )


# Close the driver
driver.quit()

csv_filename = f'output/{location}.csv'
# Write the output to a CSV file
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Name', 'Phone', 'Url'])
    writer.writerows(output)

print(f'Successfully scraped {len(output)} businesses.')
print("Scraping completed.")