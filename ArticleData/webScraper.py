from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import os

# Function to read links from a JSON file
def read_links_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        links = json.load(file)
    return links

# Function to initialize the Selenium WebDriver
def init_driver():
    options = Options()
    options.add_argument('--headless')  # Run in headless mode (no browser UI)
    options.add_argument('--disable-gpu')
    service = Service(executable_path='/Users/biden/PycharmProjects/AlphaVantage-MarketPrediction/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Helper function to find elements with given classes or no class
def scrape_elements_with_optional_classes(soup, tag_name, class_names=None):
    elements = []
    if class_names:
        candidates = soup.find_all(tag_name)
        for el in candidates:
            el_classes = el.get('class', [])
            if not el_classes or any(cls in el_classes for cls in class_names):
                elements.append(el)
    else:
        elements = soup.find_all(tag_name)
    return elements

# Function to scrape elements with Selenium and WebDriverWait
def scrape_with_selenium(driver, url):
    driver.get(url)
    # Wait for the page to load completely, adjust this to wait for a specific element if needed
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))  # Waiting for the 'body' tag to load
    )
    return BeautifulSoup(driver.page_source, 'html.parser')

# Function to scrape <p> elements from links
def scrape_paragraphs_from_links(driver, links, class_names=None):
    all_paragraphs = []
    for link in links:
        try:
            soup = scrape_with_selenium(driver, link)
            paragraphs = scrape_elements_with_optional_classes(soup, 'p', class_names)
            for i, p in enumerate(paragraphs):
                all_paragraphs.append({
                    "url": link,
                    "line_number": i,
                    "text": p.text.strip()
                })
        except Exception as e:
            print(f"Failed to fetch {link}: {e}")
    return all_paragraphs

# Function to scrape <div> elements from links
def scrape_divs_from_links(driver, links, class_names=None):
    all_divs = []
    for link in links:
        try:
            soup = scrape_with_selenium(driver, link)
            divs = scrape_elements_with_optional_classes(soup, 'div', class_names)
            for i, div in enumerate(divs):
                all_divs.append({
                    "url": link,
                    "line_number": i,
                    "text": div.text.strip()
                })
        except Exception as e:
            print(f"Failed to fetch {link}: {e}")
    return all_divs

# Function to scrape <h3> elements from links
def scrape_h3_from_links(driver, links, class_names=None):
    all_h3 = []
    for link in links:
        try:
            soup = scrape_with_selenium(driver, link)
            
            # Adding WebDriverWait here for <h3> elements specifically if needed
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'h3'))  # Wait until all <h3> tags are loaded
            )
            
            h3_elements = scrape_elements_with_optional_classes(soup, 'h3', class_names)
            for i, h3 in enumerate(h3_elements):
                all_h3.append({
                    "url": link,
                    "line_number": i,
                    "text": h3.text.strip()
                })
        except Exception as e:
            print(f"Failed to fetch {link}: {str(e)}")
    return all_h3

# MAIN EXECUTION
urls = read_links_from_json('links.json')
paragraph_classes = ['intro', 'highlight']  # Or set to None
div_classes = ['box', 'content']
h3_classes = ['clamp tw-line-clamp-none yf-1y7058a', 'clamp  yf-1y7058a']# Or set to None

driver = init_driver()
paragraph_objects = scrape_paragraphs_from_links(driver, urls, paragraph_classes)
div_objects = scrape_divs_from_links(driver, urls, div_classes)
h3_objects = scrape_h3_from_links(driver, urls, h3_classes)
driver.quit()

# Saving the results to JSON files
with open('paragraphs.json', 'w', encoding='utf-8') as pfile:
    json.dump(paragraph_objects, pfile, ensure_ascii=False, indent=2)

with open('divs.json', 'w', encoding='utf-8') as dfile:
    json.dump(div_objects, dfile, ensure_ascii=False, indent=2)

with open('h3.json', 'w', encoding='utf-8') as hfile:
    json.dump(h3_objects, hfile, ensure_ascii=False, indent=2)


