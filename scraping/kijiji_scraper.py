import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

# Optional: Set headers at the top so you can change them in one place
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

def build_search_url(city, keyword, page):
    # Builds the search URL for Kijiji with pagination
    return (
        f'https://www.kijiji.ca/b-buy-sell/{city}/{keyword}/page-{page}/k0c10l1700199?address={city}%2C%20AB&ll=51.04473309999999%2C-114.0718831&radius=50.0&sort=dateDesc&view=list'
    )

def fetch_html(url):
    # Fetches HTML from a URL
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_search_page(html):
    if not html:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string)
            for item in data.get("itemListElement", []):
                product = item.get("item", {})
                ad_url = product.get("url")
                posted_date = get_posted_date(ad_url)

                if posted_date:
                    results.append({
                        "title": product.get("name"),
                        "price": product.get("offers", {}).get("price"),
                        "url": ad_url,
                        "posted_date": posted_date  # keep as datetime
                    })
        except Exception:
            continue

    return results


def get_posted_date(ad_url):
    # Fetches an individual ad page and extracts the posted date
    html = fetch_html(ad_url)
    if not html:
        return None
    
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and "validFrom" in data:
                return datetime.strptime(data["validFrom"][:10], "%Y-%m-%d")
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "validFrom" in item:
                        return datetime.strptime(item["validFrom"][:10], "%Y-%m-%d")
        except Exception:
            continue
    
    # Fallback: regex
    match = re.search(r'"validFrom"\s*:\s*"([^"]+)"', html)
    if match:
        return datetime.strptime(match.group(1)[:10], "%Y-%m-%d")

    return None

def save_results(ads, page):
    filename = f"data/cache/page-{page}-results.json"
    try:
        ads_to_save = []
        for ad in ads:
            ad_copy = ad.copy()
            ad_copy["posted_date"] = ad_copy["posted_date"].strftime("%Y-%m-%d")
            ads_to_save.append(ad_copy)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(ads_to_save, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(ads)} ads to {filename}")
    except Exception as e:
        print(f"Error saving results: {e}")




























#############gpt helped me with this code#############
# import datetime
# import requests
# import json
# from bs4 import BeautifulSoup
# import re
# import time

# HEADERS = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/122.0.0.0 Safari/537.36"
#     )
# }

# def build_search_url(city, keyword, page):
#     # Generate Kijiji search URL
#     return (
#         f'https://www.kijiji.ca/b-buy-sell/{city}/{keyword}/page-{page}/k0c10l1700199'
#         f'?address={city}%2C%20AB&ll=51.04473309999999%2C-114.0718831&radius=50.0'
#         f'&sort=dateDesc&view=list'
#     )

# def fetch_html(url):
#     # Fetch raw HTML from URL
#     response = requests.get(url, headers=HEADERS)
#     response.raise_for_status()
#     return response.text

# def get_posted_date(ad_url):
#     # Get posted date from ad page
#     html = fetch_html(ad_url)
#     soup = BeautifulSoup(html, "html.parser")
#     for script in soup.find_all("script", {"type": "application/ld+json"}):
#         try:
#             data = json.loads(script.string)
#             if isinstance(data, dict) and "validFrom" in data:
#                 return data["validFrom"]
#             elif isinstance(data, list):
#                 for item in data:
#                     if isinstance(item, dict) and "validFrom" in item:
#                         return item["validFrom"]
#         except:
#             continue
#     match = re.search(r'"validFrom"\s*:\s*"([^"]+)"', html)
#     if match:
#         return match.group(1)
#     return None

# def parse_search_page(html, since_date):
#     # Extract listings newer than since_date
#     soup = BeautifulSoup(html, "html.parser")
#     results = []
#     stop = False
#     for script in soup.find_all("script", {"type": "application/ld+json"}):
#         try:
#             data = json.loads(script.string)
#             for item in data.get("itemListElement", []):
#                 product = item.get("item", {})
#                 ad_url = product.get("url")
#                 posted_str = get_posted_date(ad_url)
#                 if posted_str:
#                     posted_date = datetime.datetime.strptime(posted_str[:10], "%Y-%m-%d")
#                     if posted_date >= since_date:
#                         results.append({
#                             "title": product.get("name"),
#                             "description": product.get("description"),
#                             "image": product.get("image"),
#                             "url": ad_url,
#                             "price": product.get("offers", {}).get("price"),
#                             "posted_date": posted_date.strftime("%Y-%m-%d"),
#                         })
#                     else:
#                         stop = True
#                         break
#                 time.sleep(1)  # Delay between ad fetches
#             if stop:
#                 break
#         except:
#             continue
#     return results, stop

# def fetch_recent_listings(city, keyword, since_date_str):
#     # Fetch pages until all listings are older than since_date
#     since_date = datetime.datetime.strptime(since_date_str, "%Y-%m-%d")
#     all_results = []
#     page = 1
#     while True:
#         print(f"Fetching page {page}...")
#         url = build_search_url(city, keyword, page)
#         html = fetch_html(url)
#         results, stop = parse_search_page(html, since_date)
#         if not results:
#             print(f"No recent listings found on page {page}. Stopping.")
#             break
#         all_results.extend(results)
#         if stop:
#             print(f"Older listings found on page {page}. Stopping.")
#             break
#         page += 1
#         time.sleep(2)  # Delay between pages
#     now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     filename = f"data/cache/{now}-recent.json"
#     with open(filename, "w", encoding="utf-8") as f:
#         json.dump(all_results, f, ensure_ascii=False, indent=2)
#     print(f"Saved {len(all_results)} listings to {filename}")

# # Example:
# # fetch_recent_listings("calgary", "bike", "2024-06-01")





















################################### My old code ###################################
# import datetime
# import requests
# import json
# from bs4 import BeautifulSoup
# import re
# import time

# headers = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/122.0.0.0 Safari/537.36"
#     )
# }

# def fetch_search_html(city, keyword, since_date, page:int):
#     currentTime = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
#     since = datetime.datetime.strptime(since_date, "%Y-%m-%d")
#     results = []

#     url = f'https://www.kijiji.ca/b-buy-sell/{city}/{keyword}/page-{page}/k0c10l1700199?address={city}%2C%20AB&ll=51.04473309999999%2C-114.0718831&radius=50.0&sort=dateDesc&view=list'
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.text, "html.parser")

#     for script in soup.find_all("script", {"type": "application/ld+json"}):
#         try:
#             data = json.loads(script.string)
#             for item in data["itemListElement"]:
#                 product = item["item"]
#                 ad_url = product.get("url")

#                 posted_date = get_kijiji_posted_date(ad_url)
#                 if posted_date:
#                     try:
#                         posted_date = datetime.datetime.strptime(posted_date[:10], "%Y-%m-%d")
#                         if posted_date >= since:
#                             listing = {
#                                 "title": product.get("name"),
#                                 "description": product.get("description"),
#                                 "image": product.get("image"),
#                                 "url": product.get("url"),
#                                 "price": product.get("offers", {}).get("price"),
#                                 "posted_date": posted_date.strftime("%Y-%m-%d"),
#                             }
#                             results.append(listing)
#                     except Exception as e:
#                         continue
#                 time.sleep(1)  # Be polite and avoid hitting the server too hard
#         except Exception:
#             continue
    
#     #save results to a file
#     with open(f'data/cache/{currentTime}-page-{page}-raw.json', "w", encoding="utf-8") as f:
#         json.dump(results, f, ensure_ascii=False, indent=2)
#     print(f'Search for page {page} complete.')
#     print(f'{len(results)} searches found.')
#     return results
    

    
# def with_range_fetch_search_html(city, keyword, since_date, page:int = None, min_page:int = None, max_page:int = None):
#     if page is not None:
#         print(f"Fetching page {page} for {keyword} in {city}")
#         fetch_search_html(city, keyword, since_date ,page)
#         print(f"Page {page} fetched successfully.")
#         return
    
#     #Else, work wit page range
#     if min_page is None:
#         min_page = 1
#     if max_page is None:
#         max_page = 10

#     #Validate page range
#     if min_page > max_page:
#         print("Invalid page range: min_page cannot be greater than max_page.")
#         return
    
#     #loop through the page range
#     for p in range(min_page, max_page + 1):
#         print(f"Fetching page {p} of {max_page} for {keyword} in {city}...")
#         fetch_search_html(city, keyword, since_date, p)
#         print(f"Completed fetching page {p}.")
#         print(f"All pages from {min_page} to {max_page} fetched for {keyword} in {city}.")

# def get_kijiji_posted_date(url):
#     # Download the page
#     headers = {
#         "User-Agent": "Mozilla/5.0"  # Kijiji blocks some bots without this
#     }
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()

#     # Parse HTML
#     soup = BeautifulSoup(response.text, "html.parser")

#     # Find <script type="application/ld+json">
#     for script in soup.find_all("script", type="application/ld+json"):
#         try:
#             data = json.loads(script.string)
#             # Sometimes it's a list, sometimes a dict
#             if isinstance(data, dict) and "validFrom" in data:
#                 return data["validFrom"]
#             elif isinstance(data, list):
#                 for item in data:
#                     if isinstance(item, dict) and "validFrom" in item:
#                         return item["validFrom"]
#         except Exception:
#             continue

#     # Fallback: Search for 'validFrom' in raw HTML if schema missing
#     match = re.search(r'"validFrom"\s*:\s*"([^"]+)"', response.text)
#     if match:
#         return match.group(1)

#     return None



# # Example usage:
# url = "https://www.kijiji.ca/v-bike-clothes-shoes-accessories/calgary/brand-new-bike-multi-tool/1718408999"
# posted_date = get_kijiji_posted_date(url)
# if posted_date:
#     print(f"Date posted: {posted_date}")
# else:
#     print("Could not find posted date.")