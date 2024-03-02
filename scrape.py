import requests
from bs4 import BeautifulSoup
import sys
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

proxies = {
    'http': 'http://50.145.6.38:80'
}

def scrape_manga_info(url):
    response = requests.get(url, headers=headers, proxies=proxies)
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

    # Extract language
    language_element = soup.find('td', class_='gdt1', string='Language:')
    language = language_element.find_next_sibling('td').text.strip() if language_element else "Language not found"

    return manga_name, group_name, artist_name, language

def clean_manga_name(manga_name, group_name, artist_name):
    # Remove group name and artist name from manga name if they are surrounded by [] or ()
    pattern = r"\[[^\]]*\]|\([^\)]*\)"
    manga_name = re.sub(pattern, "", manga_name)
    manga_name = manga_name.strip()

    return manga_name

def search_mangas_by_artist(artist_name):
    base_url = ""
    search_url = base_url + artist_name.replace(" ", "+")
    print ("search_url: "+search_url)
    response = requests.get(search_url)
    if response.status_code != 200:
        print("Failed to fetch the webpage. Status code:", response.status_code)
        return []
    print ("response:" + response.text)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract list of other mangas by the artist
    manga_list = []
    results = soup.find_all('div', class_='gl1t')
    
    for result in results:
        
        manga_title = result.find('div', class_='gl3c').text.strip()
        manga_list.append(manga_title)

    return manga_list


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    manga_name, group_name, artist_name, language = scrape_manga_info(url)
    cleaned_manga_name = clean_manga_name(manga_name, group_name, artist_name)

    print("Manga Name:", manga_name)
    print("Group Name:", group_name)
    print("Artist Name:", artist_name)
    print("Language:", language)
    print("Cleaned Manga Name:", cleaned_manga_name)

    artist_name = "shayo"
    print(f"Other mangas by {artist_name}:")
    manga_list = search_mangas_by_artist(artist_name)
    for manga_title in manga_list:
        print(manga_title)
