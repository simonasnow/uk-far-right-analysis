import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time
from newspaper import Article, Config
import yaml

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ArticleExtractor/1.0)"}
CONFIG = yaml.safe_load(open("config.yml"))
BASE_URL = CONFIG['website']

def get_links_from_homepage():
    """Extract links from the homepage."""
    response = requests.get(BASE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    links = set()
#     print(soup)

    for a in soup.find_all("a", href=True):
        href = a["href"]
      
        # extraction of all urls published in the website
        if href.startswith("/"):
            href = urljoin(BASE_URL, href)

        # extraction of autoreferencial urls 
        if href.startswith(BASE_URL):
            links.add(href)
    
    # remove href e.g., https://www.patrioticalternative.org.uk/users/facebook/connect?page_id=16&amp;scope=public_profile%2Cemail
    links = [x for x in links if 'facebook' not in x]

    return links

def get_links_from_section(url_section, tot_page):
    """Extract article links from specific sections of the website."""
    links = set()
    for page_number in range(1,tot_page):
        url = url_section+CONFIG['page_prefix']+str(page_number)
        links.add(url)
    
    return list(links)

def extract_article(url):
      """Extract article content from a single URL."""
      try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()        
            soup = BeautifulSoup(response.text, "html.parser")
            #   print(soup.prettify)

            # the newspaper library gets cleaned results
            config = Config()
            config.browser_user_agent = HEADERS['User-Agent']
            news_article  = Article(url, config=config)
            news_article .download()
            news_article .parse()
            date = news_article.publish_date
            title = news_article .title
            article_text = news_article .text
            images = list(news_article.images)
            videos = list(news_article.movies)
            # print(title, '\n', date, '\n', article_text)
            
            # if the main information is not retrieved, we rely on the beautiful soap library
            if not title:        
                  title = soup.title.string
                  # print('title:', title)

            if not date:
                  time_tag = soup.find("span", {"class": "lead"})
                  if time_tag:
                        date = time_tag.get_text(strip=True)
                  else:
                        date = 0
                  # print('date: ', date)

            if not article_text:
                  divs = soup.find_all('div', {"class":'row'})
                  paragraphs = []
                  for div in divs:
                        paragraph = "\n".join(p.get_text(" ", strip=True) for p in div.find_all("p"))
                        paragraphs.append(paragraph)
                  article_text = "\n".join(paragraphs)
                  # print(article_text)

            if len(images) ==0:
                  images = set()
                  for img in soup.find_all("img"):
                        img_url = img.get("src")
                        if not img_url:
                              continue

                  img_url = urljoin(url, img_url)
                  images.add(img_url)
                  images = list(images) #type set() cannot be saved in json

            if title and article_text:
                  return {
                  "url": url,
                  "title": title,
                  "date": date,
                  "content": article_text,
                  "images": images, 
                  "videos": videos
            }
            else:
                  return {
                  "url": url,
                  "title": '',
                  "date": date,
                  "content": '',
                  "images": images,
                  "videos": videos
            } 
      except Exception as e:
            print('<--->',e, url)

def main():
    print("Collecting URLs...")
    urls= get_links_from_homepage()

    # extract only relevant data from specific sections:
    url_sections = CONFIG['url_sections']
    urls = [x for x in urls if x not in url_sections]
    print("Collecting URLs from ", url_sections)
    for n, sec in zip(CONFIG['tot_pages'], url_sections):
        urls = urls+get_links_from_section(sec, n+1)
    
    urls = sorted(urls)
    print(len(urls))

    results = []
    for i, url in enumerate(urls):
        
        print(f"Processing:{i} - {url}")
        article = extract_article(url)
        if article:
            results.append(article)

        time.sleep(2)

    results = list(results)
    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(results)} articles to articles.json")


if __name__ == "__main__":
    main()
