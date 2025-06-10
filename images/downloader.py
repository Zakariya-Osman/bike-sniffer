import requests
import json
from pathlib import Path
    

##NOT MY CODE
def get_image_urls_from_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)  # List of dicts

    for item in data:
        image_url = item.get("image")
        if image_url:
            print(image_url)

def get_all_image_urls():
    folder = Path('data/cache')

    for file in folder.glob('*.json'):
        print(f"--- {file.name} ---")
        with open(file, 'r') as f:
            data = json.load(f)

        for item in data:
            image_url = item.get("image")
            if image_url:
                print(image_url)

def download_image(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(filename, "wb") as f:
            f.write(response.content)

        print(f"Image downloaded and saved as {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloaded image: {e}")

# image_url = 'https://media.kijiji.ca/api/v1/ca-prod-fsbo-ads/images/b0/b08c10bc-67dc-4818-8a4d-239600236270?rule=kijijica-200-jpg'
# download_image(image_url,'/images/downloaded/downloaded.png')
