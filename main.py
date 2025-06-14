from scraping.kijiji_scraper import build_search_url, fetch_html, parse_search_page, save_results
from datetime import datetime
import time

# Define cutoff date
SINCE_DATE = datetime.strptime("2025-06-12", "%Y-%m-%d") 

def run_scraper():
    city = "calgary"
    keyword = "bike"
    page = 1
    while True:
        url = build_search_url(city, keyword, page)
        html = fetch_html(url)
        ads = parse_search_page(html)

        if not ads:
            print(f"No ads found on page {page}. Stopping.")
            break

        fresh_ads = [ad for ad in ads if ad['posted_date'] >= SINCE_DATE]

        # Check if all ads are too old
        if not fresh_ads:
            print(f"No fresh ads on page {page}. Stopping.")
            break

        save_results(fresh_ads, page)
        print(f"Saved {len(fresh_ads)} fresh ads from page {page}")

        page += 1
        time.sleep(2)  # Being polite to the server

if __name__ == "__main__":
    run_scraper()