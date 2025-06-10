import datetime
import requests
import json
from bs4 import BeautifulSoup

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

def fetch_search_html(city, keyword, page:int):
    currentTime = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    results = []
    url = f'https://www.kijiji.ca/b-buy-sell/{city}/{keyword}/page-{page}/k0c10l1700199?address={city}%2C%20AB&ll=51.04473309999999%2C-114.0718831&radius=50.0&sort=dateDesc&view=list'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string)
            for item in data["itemListElement"]:
                product = item["item"]
                listing = {
                    "title": product.get("name"),
                    "description": product.get("description"),
                    "image": product.get("image"),
                    "url": product.get("url"),
                    "price": product.get("offers", {}).get("price"),
                }
                results.append(listing)
        except Exception as e:
            continue
    with open(f'data/cache/{currentTime}-page-{page}-raw.json', "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'Search for page {page} complete.')
    print(f'{len(results)} searches found.')
    return results
    

    
def with_range_fetch_search_html(city, keyword, page:int = None, min_page:int = None, max_page:int = None):
    if page is not None:
        print(f"Fetching page {page} for {keyword} in {city}")
        fetch_search_html(city, keyword, page)
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
        fetch_search_html(city, keyword, p)
        print(f"Completed fetching page {p}.")
        print(f"All pages from {min_page} to {max_page} fetched for {keyword} in {city}.")

