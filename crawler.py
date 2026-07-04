import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from contact_utils import extract_phone_from_text, extract_address_from_text


def crawl_website(base_url, max_pages=10):
    """
    Crawl a website and collect content from multiple pages.

    Args:
        base_url (str): Starting URL of the website.
        max_pages (int): Maximum number of pages to crawl.

    Returns:
        dict: Page name -> text content collected from the crawled pages.
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
        except Exception:
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
        except Exception:
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


def extract_contact_info(all_content):
    """
    Best-effort extraction of a phone number and postal address from crawled
    page text. Checks the 'contact' page first (most likely to have this
    info), then falls back to scanning every other crawled page.

    Args:
        all_content (dict): Output of crawl_website() — page name -> text.

    Returns:
        dict: {"phone": str, "address": str}, "N/A" when nothing is found.
    """
    if not isinstance(all_content, dict) or not all_content:
        return {"phone": "N/A", "address": "N/A"}

    priority_keys = [k for k in all_content if 'contact' in k.lower()]
    other_keys = [k for k in all_content if k not in priority_keys]

    # Scan contact page(s) first — highest chance of an accurate match
    for key in priority_keys:
        text = all_content.get(key, "")
        phone = extract_phone_from_text(text)
        address = extract_address_from_text(text)
        if phone != "N/A" or address != "N/A":
            return {
                "phone": phone,
                "address": address,
            }

    # Fall back to scanning every other page
    combined_text = " ".join(all_content.get(k, "") for k in other_keys)
    return {
        "phone": extract_phone_from_text(combined_text),
        "address": extract_address_from_text(combined_text),
    }