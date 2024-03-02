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

def check_ip_banned(response):
    if "Your IP address has been temporarily banned for excessive pageloads." in response.text:
        print("IP address banned. Please try again later.")
        return True
    return False

def extract_manga_info_from_table(table):
    manga_list = []
    if table:
        while True:
            results = table.find_all('div', class_='glink')
            for result in results:
                manga_title = result.text.strip()
                # Get the parent <a> element
                parent_a = result.parent
                manga_link = parent_a['href']
                # Extract language information
                manga_info = {'title': manga_title, 'link': manga_link}
                language_elements = parent_a.find_all('div', class_='gt')
                for element in language_elements:
                    if 'language:translated' in element['title']:
                        manga_info['translated'] = True
                    elif 'language:' in element['title'] and not 'language:translated' in element['title']:
                        manga_info['language'] = element['title'].split(':')[-1]

                manga_list.append(manga_info)
            
            # Check for next button
            next_button = table.find_next_sibling('div', class_='c2').find('a', id='dnext')
            if not next_button or not next_button.get('href'):
                break

            # Fetch next page
            next_url = next_button['href']
            response = requests.get(next_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_='itg gltc')
    else:
        print("Table not found")

    return manga_list

def search_manga_by_artist_and_word(artist_name, word_to_search):
    base_url = ""
    search_url = base_url + "artist%3A" + artist_name.replace(" ", "+") + "%24+" + word_to_search.replace(" ", "+")
    response = requests.get(search_url)
    if response.status_code != 200:
        print("Failed to fetch the webpage. Status code:", response.status_code)
        return []

    if check_ip_banned(response):
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', class_='itg gltc')
    return extract_manga_info_from_table(table)

def search_mangas_by_artist(artist_name):
    base_url = ""
    search_url = base_url + artist_name.replace(" ", "+")
    response = requests.get(search_url)
    if response.status_code != 200:
        print("Failed to fetch the webpage. Status code:", response.status_code)
        return []
    
    if check_ip_banned(response):
        return []
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Extract list of other mangas by the artist
    manga_list = []
    table = soup.find('table', class_='itg gltc')
    return extract_manga_info_from_table(table)


if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print("Usage: python script.py <url>")
    #     sys.exit(1)

    # url = sys.argv[1]
    # manga_name, group_name, artist_name, language = scrape_manga_info(url)
    # cleaned_manga_name = clean_manga_name(manga_name, group_name, artist_name)

    # print("Manga Name:", manga_name)
    # print("Group Name:", group_name)
    # print("Artist Name:", artist_name)
    # print("Language:", language)
    # print("Cleaned Manga Name:", cleaned_manga_name)

    artist_name = ""
    print(f"Other mangas by {artist_name}:")
    manga_list = search_mangas_by_artist(artist_name)
    print(len(manga_list))
    for manga_info in manga_list:
        if manga_info.get('translated') == True:
            print(manga_info)
