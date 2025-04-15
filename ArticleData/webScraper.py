import requests
from bs4 import BeautifulSoup
import json

# Function to read links from a JSON file
def read_links_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        links = json.load(file)
    return links

# Function to scrape paragraphs from a list of links
def scrape_paragraphs_from_links(links):
    all_paragraphs = []

    for link in links:
        try:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = [p.text.strip() for p in soup.find_all('p')]
            print(paragraphs)
            # Save each paragraph as an object with link and line number
            for i, paragraph in enumerate(paragraphs):
                all_paragraphs.append({
                    "url": link,
                    "line_number": i,
                    "text": paragraph
                })

        except requests.RequestException as e:
            print(f"Failed to fetch {link}: {e}")

    return all_paragraphs

# Load the list of URLs
urls = read_links_from_json('links.json')

# Scrape and collect paragraph objects
paragraph_objects = scrape_paragraphs_from_links(urls)

# Save to a JSON file
with open('paragraphs.json', 'w', encoding='utf-8') as file:
    json.dump(paragraph_objects, file, ensure_ascii=False, indent=2)