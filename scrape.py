import requests
from bs4 import BeautifulSoup
import sys
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}



def scrape_manga_info(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch the webpage. Status code:", response.status_code)
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract manga name
    manga_name_element = soup.find('h1', id='gn')
    manga_name = manga_name_element.text.strip() if manga_name_element else "Manga name not found"

    # Extract group name
    group_name_element = soup.find('a', href=lambda x: x and 'group' in x)
    group_name = group_name_element.text.strip() if group_name_element else "Group name not found"

    # Extract artist name
    artist_name_element = soup.find('a', href=lambda x: x and 'artist' in x)
    artist_name = artist_name_element.text.strip() if artist_name_element else "Artist name not found"

    return manga_name, group_name, artist_name

def clean_manga_name(manga_name, group_name, artist_name):
    # Remove group name and artist name from manga name if they are surrounded by [] or ()
    pattern = r"\[[^\]]*\]|\([^\)]*\)"
    manga_name = re.sub(pattern, "", manga_name)
    manga_name = manga_name.strip()

    return manga_name


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    manga_name, group_name, artist_name = scrape_manga_info(url)
    cleaned_manga_name = clean_manga_name(manga_name, group_name, artist_name)

    print("Manga Name:", manga_name)
    print("Group Name:", group_name)
    print("Artist Name:", artist_name)
    print("Cleaned Manga Name:", cleaned_manga_name)
