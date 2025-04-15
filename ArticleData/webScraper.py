import requests
from bs4 import BeautifulSoup
import json

# Function to read links from a JSON file
def read_links_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        links = json.load(file)
    return links

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

# Function to scrape <p> elements from links
def scrape_paragraphs_from_links(links, class_names=None):
    all_paragraphs = []

    for link in links:
        try:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')

            paragraphs = scrape_elements_with_optional_classes(soup, 'p', class_names)

            for i, p in enumerate(paragraphs):
                all_paragraphs.append({
                    "url": link,
                    "line_number": i,
                    "text": p.text.strip()
                })

        except requests.RequestException as e:
            print(f"Failed to fetch {link}: {e}")

    return all_paragraphs

# Function to scrape <div> elements from links
def scrape_divs_from_links(links, class_names=None):
    all_divs = []

    for link in links:
        try:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')

            divs = scrape_elements_with_optional_classes(soup, 'div', class_names)

            for i, div in enumerate(divs):
                all_divs.append({
                    "url": link,
                    "line_number": i,
                    "text": div.text.strip()
                })

        except requests.RequestException as e:
            print(f"Failed to fetch {link}: {e}")

    return all_divs

# Step 1: Load URLs
urls = read_links_from_json('links.json')

# Step 2: Scrape with class filters (you can adjust or leave as None)
paragraph_classes = ['intro', 'highlight']  # or set to None
div_classes = ['box', 'content']            # or set to None

paragraph_objects = scrape_paragraphs_from_links(urls, paragraph_classes)
div_objects = scrape_divs_from_links(urls, div_classes)

# Step 3: Save to JSON files
with open('paragraphs.json', 'w', encoding='utf-8') as pfile:
    json.dump(paragraph_objects, pfile, ensure_ascii=False, indent=2)

with open('divs.json', 'w', encoding='utf-8') as dfile:
    json.dump(div_objects, dfile, ensure_ascii=False, indent=2)
