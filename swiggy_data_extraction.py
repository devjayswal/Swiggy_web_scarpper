import os
import csv
import random
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
from bs4 import BeautifulSoup

# Define the relative path
path_to_file = "/home/era/Desktop/Work/cronjobs/Swiggy_web_scarppers/"

# Ensure the directory exists
if not os.path.exists(path_to_file):
    os.makedirs(path_to_file)

mode = ""  # mode=extract/scrape/""

def setup_driver():
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--disable-dev-shm-usage')
    firefox_options.add_argument('--ignore-ssl-errors=yes')
    firefox_options.add_argument('--ignore-certificate-errors')
    firefox_options.add_argument('--disable-gpu')
    firefox_options.add_argument('--disable-extensions')
    firefox_options.add_argument('--disable-software-rasterizer')
    firefox_options.binary_location = "/usr/bin/firefox"  # Specify Firefox binary path
    
    print("Setting up FirefoxDriver...")
    try:
        driver = webdriver.Firefox(options=firefox_options)
        print("FirefoxDriver setup successful")
        return driver
    except Exception as e:
        print(f"Error setting up FirefoxDriver: {e}")
        return None    

def extract_offers(driver, url):
    temp_offers = []
    try:
        driver.get(url)
        
        # Try to find and modify the "row" element
        try:
            element = driver.find_element(By.CLASS_NAME, "row")
            driver.execute_script("arguments[0].classList.remove('row');", element)
        except Exception as e:
            print(f"Error finding or modifying 'row' element: {e}")
            # Continue execution even if this fails
        
        # Try to find and process offer elements
        try:
            title = driver.execute_script("return document.querySelector('.sc-aXZVg.cNRZhA')")
            elements = driver.execute_script("return document.querySelectorAll('.sc-hHOBiw.hKJHKQ');")
            for idx, element in enumerate(elements):
                print(idx)
                try:
                    element.click()
                    
                    # Wait for the text element to be visible and log its text
                    text_elem = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, '.sc-aXZVg.cKDIFf.sc-eNSrOW.htXejL'))
                    )
                    temp = {}
                    temp['Restaurant'] = title.text
                    temp['Offers'] = text_elem.text
                    temp_offers.append(temp)
                    
                    close_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '.sc-dtInlm.caGqNi'))
                    )
                    close_button.click()
                    print('Modal closed')
                    time.sleep(random.uniform(2, 4))
                except Exception as e:
                    print(f"Error processing offer {idx}: {e}")
                    # Continue to next offer even if this one fails
                    time.sleep(random.uniform(2, 4))
        except Exception as e:
            print(f"Error finding offer elements in {url}: {e}")
    
    except Exception as e:
        print(f"An unexpected error occurred in {url}: {e}")
    
    if not temp_offers:
        print('No offers found')
    
    return temp_offers

def extract_offers_modified(url):
    driver = setup_driver()
    driver.get(url)
    try:
        print('try')
        time.sleep(random.uniform(2, 5))
    except Exception as e:
        print("No offers found")
        print(e)

def process_url(url):
    print(f"Processing URL: {url}")
    
    if mode != "extract":
        driver = setup_driver()
        if driver is None:
            print(f"Skipping URL due to driver initialization failure: {url}")
            return []
        
        driver.get(url)
        driver.maximize_window()
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "jXGZuP"))
        )
        print('Page loaded')
        time.sleep(random.uniform(1, 3))
        driver.execute_script("window.scrollBy(0, 1500);")
        try:
            t1 = time.time()
            time.sleep(random.uniform(2, 4))
            
            while True:
                try:
                    show_more_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".InfoCard__Container-sc-16vtyhn-0.fBowAU"))
                    )
                    
                    driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
                    driver.execute_script("arguments[0].click();", show_more_button)
                    print('Button clicked')
                    time.sleep(random.uniform(3, 5))
                    
                    if time.time() - t1 > 10:
                        break
                    driver.execute_script("window.scrollBy(0, 1000);")
                except TimeoutException:
                    print('No more "show more" buttons found, exiting loop.')
                    break

            page_source = driver.page_source    
            with open(os.path.join(path_to_file, 'check.txt'), 'w+') as f:
                f.write(page_source)
            print('Source saved')
            soup = BeautifulSoup(page_source, features='lxml')
            grid = soup.find('div', class_='sc-gLLvby jXGZuP')
            a_tags = grid.find_all('a')
            fp = open(os.path.join(path_to_file, 'resto_links.csv'), 'a+')
            for tag in a_tags:
                print(tag['href'])
                fp.write(f"{tag['href']}\n")
            print('Prospect done')
            fp.close()
            
            return os.path.join(path_to_file, 'resto_links.csv')
        
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            return " "
        
        finally:
            driver.quit()

def extract_dishes_data(url):
    print(f"Processing URL: {url}")
    
    if mode != "extract":
        driver = setup_driver()
        if driver is None:
            print(f"Skipping URL due to driver initialization failure: {url}")
            return []
        
        driver.get(url)
        driver.maximize_window()
        time.sleep(random.uniform(3, 5))
        print('Page loaded')
        
        try:
            page_source = driver.page_source    
            with open(os.path.join(path_to_file, 'check1.txt'), 'w+') as f:
                f.write(page_source)
            print('Source saved')
            soup = BeautifulSoup(page_source, features='lxml')
            grids = soup.find_all('div', class_='sc-fxwrCY laJkOR')
            print(f"Length of grid: {len(grids)}")
            resto_data = []
            resto_name = soup.find('h1', class_ = 'sc-aXZVg cNRZhA')
            resto_data_text = resto_name.text.strip() if resto_name else None
            
            for grid in grids:
                data = {}
                # restaurant name
                data['Restaurant'] = resto_data_text
                # name
                name = grid.find('div', class_='sc-aXZVg cjJTeQ sc-hIUJlX gCYyvX')
                name_text = name.text.strip() if name else None
                data['Name'] = name_text
                # price
                price = grid.find('div', class_='sc-aXZVg kCbDOU')
                price_text = price.text.strip() if price else None
                data['Price'] = price_text
                # rating
                rating = grid.find('div', class_='sc-aXZVg cFwhHc sc-krNlru borGNh')
                rating_text = rating.text.strip() if rating else None
                data['Rating'] = rating_text
                # number of reviews
                no_of_review = grid.find('div', class_='sc-aXZVg jmwKWP')
                no_of_review_text = no_of_review.text.strip() if no_of_review else None
                data['No_of_reviews'] = no_of_review_text
                resto_data.append(data)
            
            return resto_data
        
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            return " "
        
        finally:
            driver.quit()
    
    return []

def main():
    path_of_resto_link = process_url('https://www.swiggy.com/city/lucknow') 

    urls = []
    with open(os.path.join(path_to_file, 'resto_links.csv'), 'r') as offer_file:
        csv_reader = csv.reader(offer_file)
        for row in csv_reader:
            if row:
                urls.append(row[0].strip())
    resto_data_list = []
    for url in urls:
        data = extract_dishes_data(url)
        print(data)
        df = pd.DataFrame(data)
        df.to_csv(os.path.join(path_to_file, 'resto_data.csv'), mode='a', sep=',', index=False, header=False)

if __name__ == "__main__":
    main()
