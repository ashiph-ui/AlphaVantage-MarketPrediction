import requests
from bs4 import BeautifulSoup
import json

# Function to read links from a JSON file
def read_links_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        links = json.load(file)
    return links

# Function to scrape <p> elements from a list of links
def scrape_paragraphs_from_links(links):
    all_paragraphs = []

    for link in links:
        try:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = [p.text.strip() for p in soup.find_all('p')]

            for i, paragraph in enumerate(paragraphs):
                all_paragraphs.append({
                    "url": link,
                    "line_number": i,
                    "text": paragraph
                })

        except requests.RequestException as e:
            print(f"Failed to fetch {link}: {e}")

    return all_paragraphs

# Function to scrape <div> elements from a list of links
def scrape_divs_from_links(links):
    all_divs = []

    for link in links:
        try:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            divs = [div.text.strip() for div in soup.find_all('div')]

            for i, div_text in enumerate(divs):
                all_divs.append({
                    "url": link,
                    "line_number": i,
                    "text": div_text
                })

        except requests.RequestException as e:
            print(f"Failed to fetch {link}: {e}")

    return all_divs

# Step 1: Load URLs from the file
urls = read_links_from_json('links.json')

# Step 2: Scrape <p> and <div> elements
paragraph_objects = scrape_paragraphs_from_links(urls)
div_objects = scrape_divs_from_links(urls)

# Step 3: Save them to separate JSON files
with open('paragraphs.json', 'w', encoding='utf-8') as pfile:
    json.dump(paragraph_objects, pfile, ensure_ascii=False, indent=2)

with open('divs.json', 'w', encoding='utf-8') as dfile:
    json.dump(div_objects, dfile, ensure_ascii=False, indent=2)
