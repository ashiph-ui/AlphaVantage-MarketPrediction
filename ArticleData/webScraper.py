from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
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
    service = Service(executable_path='C:\Users\biden\PycharmProjects\AlphaVantage-MarketPrediction\chromedriver.exe')
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

# Function to scrape elements with Selenium
def scrape_with_selenium(driver, url):
    driver.get(url)
    time.sleep(3)  # Wait for page to load
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

# MAIN EXECUTION
urls = read_links_from_json('links.json')
paragraph_classes = ['intro', 'highlight']  # Or set to None
div_classes = ['box', 'content']            # Or set to None

driver = init_driver()
paragraph_objects = scrape_paragraphs_from_links(driver, urls, paragraph_classes)
div_objects = scrape_divs_from_links(driver, urls, div_classes)
driver.quit()

with open('paragraphs.json', 'w', encoding='utf-8') as pfile:
    json.dump(paragraph_objects, pfile, ensure_ascii=False, indent=2)

with open('divs.json', 'w', encoding='utf-8') as dfile:
    json.dump(div_objects, dfile, ensure_ascii=False, indent=2)

