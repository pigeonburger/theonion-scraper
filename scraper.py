import re
import time
import requests
from threading import Thread
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0'
}

def parse_sitemap():
    global urls
    print('Scanning sitemap.......')
    base = 'https://www.theonion.com'
    r = requests.get(base+'/sitemap', headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    months = soup.find_all('a', class_='js_sitemap-month')

    urls = []
    for month in months:
        t = Thread(target=get_sitemap_links, args=(month,))
        t.daemon = True
        t.start()
        time.sleep(0.1)
        

        print(f'Found {len(urls)} articles', end='\r')
    print()
    return urls

def get_sitemap_links(month):
    base = 'https://www.theonion.com'
    month_url = base+month['href']
    r = requests.get(month_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    article_links = [i.find('a')['href'] for i in soup.find_all('h4', class_='js_sitemap-article')]
    urls.extend(article_links)

def get_article_content(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    try:
        title = soup.find('h1', class_='bBLibw').encode_contents().decode('utf-8')

        content = soup.find('div', class_='js_post-content').find_all('p')
        if content == []:
            h = None
        article_content = [re.sub('<[^<]+?>', '', i.encode_contents().decode('utf-8')) for i in content]
        article_content.insert(0, title)
        h = '\n\n'.join(article_content)
    except:
        h = None
    
    if h != None:
        print(f'Fetched {urls.index(url) + 1} of {len(urls)} articles......', end='\r')
        with open('theonioncontent.txt', 'a+', encoding='utf-8') as contentfile:
            contentfile.write('<|startoftext|>'+h+'<|endoftext|>\n')

def main():
    global urls
    urls = parse_sitemap()

    for url in urls:
        t = Thread(target=get_article_content, args=(url,))
        t.daemon = True
        t.start()
        time.sleep(0.1)
    print(f'\nDone scraping articles.')

print('The Onion Article Scraper')
print('By Pigeonburger <https://github.com/pigeonburger>, 2021')
print('--------------------------')
main()
