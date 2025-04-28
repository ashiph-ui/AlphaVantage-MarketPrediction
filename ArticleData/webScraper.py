from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import os

# Function to read links from a JSON file
def read_links_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        links = json.load(file)
    return links

# Function to initialize the Selenium WebDriver
def init_driver():
    options = Options()
    options.add_argument('--headless')
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
        if not elements:  # fallback if none found
            elements = soup.find_all(tag_name)
    else:
        elements = soup.find_all(tag_name)
    return elements

# Extract links that match certain keywords
def extract_filtered_links(soup, base_url, keywords=None):
    found_links = set()
    keywords = keywords or []

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        href = urljoin(base_url, href)  # safer than string concat
        if href.startswith('http') and any(kw in href for kw in keywords):
            found_links.add(href)
    return found_links

# Save new links to links.json
def save_new_links(new_links, filename='links.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            existing_links = set(json.load(f))
    except FileNotFoundError:
        existing_links = set()
    updated_links = list(existing_links.union(new_links))
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(updated_links, f, ensure_ascii=False, indent=2)

# Function to scrape elements with Selenium and WebDriverWait
def scrape_with_selenium(driver, url, keywords_for_links=None, wait_tag='body'):
    driver.get(url)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, wait_tag))
    )
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    if not soup or not soup.body:
        raise ValueError("No <body> tag found in page.")

    new_links = set()
    if keywords_for_links:
        new_links = extract_filtered_links(soup, url, keywords_for_links)
    return soup, new_links

# Function to scrape <p> elements from links
def scrape_paragraphs_from_links(driver, links, class_names=None, keywords_for_links=None):
    all_paragraphs = []
    all_new_links = set()

    for link in links:
        try:
            soup, new_links = scrape_with_selenium(driver, link, keywords_for_links)
            all_new_links.update(new_links)

            paragraphs = scrape_elements_with_optional_classes(soup, 'p', class_names)
            for i, p in enumerate(paragraphs):
                all_paragraphs.append({
                    "url": link,
                    "line_number": i,
                    "text": p.text.strip()
                })
        except Exception as e:
            print(f"Failed to fetch {link}: {e}")

    if all_new_links:
        save_new_links(all_new_links)

    return all_paragraphs

# Function to scrape <div> elements from links
def scrape_divs_from_links(driver, links, class_names=None):
    all_divs = []
    for link in links:
        try:
            soup, _ = scrape_with_selenium(driver, link)
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
            soup, _ = scrape_with_selenium(driver, link, wait_tag='h3')
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
paragraph_classes = ['intro', 'highlight']
div_classes = ['box', 'content']
h3_classes = ['clamp tw-line-clamp-none yf-1y7058a', 'clamp  yf-1y7058a']
keywords_to_watch = ['article', 'news', 'post']

driver = init_driver()
paragraph_objects = scrape_paragraphs_from_links(driver, urls, paragraph_classes, keywords_to_watch)
div_objects = scrape_divs_from_links(driver, urls, div_classes)
h3_objects = scrape_h3_from_links(driver, urls, h3_classes)
driver.quit()

with open('paragraphs.json', 'w', encoding='utf-8') as pfile:
    json.dump(paragraph_objects, pfile, ensure_ascii=False, indent=2)

with open('divs.json', 'w', encoding='utf-8') as dfile:
    json.dump(div_objects, dfile, ensure_ascii=False, indent=2)

with open('h3.json', 'w', encoding='utf-8') as hfile:
    json.dump(h3_objects, hfile, ensure_ascii=False, indent=2)

print(f"Scraped {len(paragraph_objects)} paragraphs, {len(div_objects)} divs, {len(h3_objects)} h3 elements.")



