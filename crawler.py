import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def crawl_website(base_url, max_pages=10):
      """
    Crawl a website and collect content from multiple pages.

    Args:
        base_url (str): Starting URL of the website.
        max_pages (int): Maximum number of pages to crawl.

    Returns:
     list: Combined text content collected from the crawled pages.
      """

      important_pages = ['about', 'products', 'services', 'solutions', 'contact', 'pricing']
      visited = set()
      all_content = {}

      def get_page_content(url):
        try:
            response = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0"
            })
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove junk
            for tag in soup(['script', 'style', 'nav', 'footer']):
                tag.decompose()
            
            text = soup.get_text(separator=' ', strip=True)
            return text[:3000]  # Limit content
        except:
            return ""

      def find_important_links(url):
        try:
            response = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0"
            })
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            
            for a in soup.find_all('a', href=True):
                href = urljoin(url, a['href'])
                parsed = urlparse(href)
                
                # Same domain only
                if parsed.netloc != urlparse(url).netloc:
                    continue
                # Ignore login/irrelevant pages    
                if any(x in href.lower() for x in ['login', 'signin', 'signup', 'cart', 'checkout']):
                    continue
                # Important pages only
                if any(page in href.lower() for page in important_pages):
                    links.append(href)
            
            return list(set(links))[:max_pages]
        except:
            return []

     # Crawl home page first
      all_content['home'] = get_page_content(base_url)
      visited.add(base_url)

      # Find and crawl important pages
      links = find_important_links(base_url)
      for link in links:
        if link not in visited:
            page_name = link.split('/')[-1] or 'page'
            all_content[page_name] = get_page_content(link)
            visited.add(link)

      return all_content