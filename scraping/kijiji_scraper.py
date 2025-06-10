import datetime
import requests
import json
from bs4 import BeautifulSoup
import re
import time

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

def fetch_search_html(city, keyword, since_date, page:int):
    currentTime = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    since = datetime.datetime.strptime(since_date, "%Y-%m-%d")
    results = []

    url = f'https://www.kijiji.ca/b-buy-sell/{city}/{keyword}/page-{page}/k0c10l1700199?address={city}%2C%20AB&ll=51.04473309999999%2C-114.0718831&radius=50.0&sort=dateDesc&view=list'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string)
            for item in data["itemListElement"]:
                product = item["item"]
                ad_url = product.get("url")

                posted_date = get_kijiji_posted_date(ad_url)
                if posted_date:
                    try:
                        posted_date = datetime.datetime.strptime(posted_date[:10], "%Y-%m-%d")
                        if posted_date >= since:
                            listing = {
                                "title": product.get("name"),
                                "description": product.get("description"),
                                "image": product.get("image"),
                                "url": product.get("url"),
                                "price": product.get("offers", {}).get("price"),
                                "posted_date": posted_date.strftime("%Y-%m-%d"),
                            }
                            results.append(listing)
                    except Exception as e:
                        continue
                time.sleep(1)  # Be polite and avoid hitting the server too hard
        except Exception:
            continue
    
    #save results to a file
    with open(f'data/cache/{currentTime}-page-{page}-raw.json', "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'Search for page {page} complete.')
    print(f'{len(results)} searches found.')
    return results
    

    
def with_range_fetch_search_html(city, keyword, since_date, page:int = None, min_page:int = None, max_page:int = None):
    if page is not None:
        print(f"Fetching page {page} for {keyword} in {city}")
        fetch_search_html(city, keyword, since_date ,page)
        print(f"Page {page} fetched successfully.")
        return
    
    #Else, work wit page range
    if min_page is None:
        min_page = 1
    if max_page is None:
        max_page = 10

    #Validate page range
    if min_page > max_page:
        print("Invalid page range: min_page cannot be greater than max_page.")
        return
    
    #loop through the page range
    for p in range(min_page, max_page + 1):
        print(f"Fetching page {p} of {max_page} for {keyword} in {city}...")
        fetch_search_html(city, keyword, since_date, p)
        print(f"Completed fetching page {p}.")
        print(f"All pages from {min_page} to {max_page} fetched for {keyword} in {city}.")

def get_kijiji_posted_date(url):
    # Download the page
    headers = {
        "User-Agent": "Mozilla/5.0"  # Kijiji blocks some bots without this
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Parse HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Find <script type="application/ld+json">
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            # Sometimes it's a list, sometimes a dict
            if isinstance(data, dict) and "validFrom" in data:
                return data["validFrom"]
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "validFrom" in item:
                        return item["validFrom"]
        except Exception:
            continue

    # Fallback: Search for 'validFrom' in raw HTML if schema missing
    match = re.search(r'"validFrom"\s*:\s*"([^"]+)"', response.text)
    if match:
        return match.group(1)

    return None



# Example usage:
url = "https://www.kijiji.ca/v-bike-clothes-shoes-accessories/calgary/brand-new-bike-multi-tool/1718408999"
posted_date = get_kijiji_posted_date(url)
if posted_date:
    print(f"Date posted: {posted_date}")
else:
    print("Could not find posted date.")