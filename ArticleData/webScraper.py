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
<<<<<<< HEAD
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    service = Service(executable_path='/Users/biden/PycharmProjects/AlphaVantage-MarketPrediction/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
=======
    try:
        options = Options()
        options.add_experimental_option("prefs", {"profile.default_content_settings_values.cookies": 2})
        options.add_argument('--headless')  # Run in headless mode (no browser UI)
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-features=CookieControls")
        service = Service(executable_path='/Users/Admin/PersonalProject/AlphaVantage-MarketPrediction/chromedriver.exe')  # For chif
        # service = Service(executable_path='/Users/biden/PycharmProjects/AlphaVantage-MarketPrediction/chromedriver.exe')  # For biden
        driver = webdriver.Chrome(service=service, options=options)
        print("Successful initialisation to driver")
    except Exception as e:
        print(f"Failed to initialise driver. Error message: {e}")
>>>>>>> 6ef337e2a8cb3e5f4ca709d482958253583463aa
    return driver

def reject_cookies(url):
    # URL and driver setup
    url = "https://finance.yahoo.com/?guccounter=1"
    service = Service(executable_path='/Users/Admin/PersonalProject/AlphaVantage-MarketPrediction/chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.get(url)

    # Wait for cookie acceptance button to appear and click it
    try:
        # Wait for the "Reject all" button to be clickable
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Reject all')]"))
        )
        button.click()
        print("Cookie acceptance declined.")
    except Exception as e:
        print("Error:", e)

    # Wait for the link to appear and click it
    try:
        # Wait for the link to be clickable
        link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='https://finance.yahoo.com/?guccounter=2']"))
        )
        link.click()
        print("Link clicked successfully.")
    except Exception as e:
        print("Error:", e)

    # Optionally, close the browser after performing actions
    time.sleep(5)  # Wait a few seconds to ensure actions are completed
    

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
    reject_cookies(url)
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
    print("Running paragraph scraper...")
    for link in links:
        try:
            print(f"Attempting to connect to {link}")
            soup, new_links = scrape_with_selenium(driver, link, keywords_for_links)
            all_new_links.update(new_links)

            paragraphs = scrape_elements_with_optional_classes(soup, 'p', class_names)
            for i, p in enumerate(paragraphs):
                all_paragraphs.append({
                    "url": link,
                    "line_number": i,
                    "text": p.text.strip()
                })
            print(f"Successfully scaped paragraph elements from {link}")
        except Exception as e:
            print(f"Failed to fetch {link}: {e}")

    if all_new_links:
        save_new_links(all_new_links)

    return all_paragraphs

# Function to scrape <div> elements from links
def scrape_divs_from_links(driver, links, class_names=None):
    all_divs = []
    print("Running div scraper...")
    for link in links:
        try:
            print(f"Attempting to connect to {link}")
            soup, _ = scrape_with_selenium(driver, link)
            divs = scrape_elements_with_optional_classes(soup, 'div', class_names)
            for i, div in enumerate(divs):
                all_divs.append({
                    "url": link,
                    "line_number": i,
                    "text": div.text.strip()
                })
            print(f"Successfully scaped div elements from {link}")
        except Exception as e:
            print(f"Failed to fetch {link}: {e}")
    return all_divs

# Function to scrape <h3> elements from links
def scrape_h3_from_links(driver, links, class_names=None):
    all_h3 = []
    print("Running h3 scraper...")
    for link in links:
        try:
<<<<<<< HEAD
            soup, _ = scrape_with_selenium(driver, link, wait_tag='h3')
=======
            print(f"Attempting to connect to {link}")
            soup, _ = scrape_with_selenium(driver, link)
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'h3'))  # Wait until all <h3> tags are loaded
            )
>>>>>>> 6ef337e2a8cb3e5f4ca709d482958253583463aa
            h3_elements = scrape_elements_with_optional_classes(soup, 'h3', class_names)
            for i, h3 in enumerate(h3_elements):
                all_h3.append({
                    "url": link,
                    "line_number": i,
                    "text": h3.text.strip()
                })
            print(f"Successfully scaped h3 elements from {link}")
        except Exception as e:
            print(f"Failed to fetch {link}: {str(e)}")
    return all_h3

# MAIN EXECUTION
<<<<<<< HEAD
urls = read_links_from_json('links.json')
paragraph_classes = ['intro', 'highlight']
=======
urls = read_links_from_json('./article-data-json/links.json')
print(urls)
paragraph_classes = ['intro', 'highlight']  # Or set to None
>>>>>>> 6ef337e2a8cb3e5f4ca709d482958253583463aa
div_classes = ['box', 'content']
h3_classes = ['clamp tw-line-clamp-none yf-1y7058a', 'clamp  yf-1y7058a']
keywords_to_watch = ['article', 'news', 'post']

driver = init_driver()

<<<<<<< HEAD
with open('paragraphs.json', 'w', encoding='utf-8') as pfile:
=======
paragraph_objects = scrape_paragraphs_from_links(driver, urls, paragraph_classes, keywords_to_watch)
with open('article-data-json/paragraphs.json', 'w', encoding='utf-8') as pfile:
>>>>>>> 6ef337e2a8cb3e5f4ca709d482958253583463aa
    json.dump(paragraph_objects, pfile, ensure_ascii=False, indent=2)

div_objects = scrape_divs_from_links(driver, urls, div_classes)
with open('article-data-json/divs.json', 'w', encoding='utf-8') as dfile:
    json.dump(div_objects, dfile, ensure_ascii=False, indent=2)

h3_objects = scrape_h3_from_links(driver, urls, h3_classes)
with open('article-data-json/h3.json', 'w', encoding='utf-8') as hfile:
    json.dump(h3_objects, hfile, ensure_ascii=False, indent=2)

<<<<<<< HEAD
print(f"Scraped {len(paragraph_objects)} paragraphs, {len(div_objects)} divs, {len(h3_objects)} h3 elements.")

=======
driver.quit()
>>>>>>> 6ef337e2a8cb3e5f4ca709d482958253583463aa


