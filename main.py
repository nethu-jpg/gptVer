import requests
import time
import logging
import os
from bs4 import BeautifulSoup
from telegram import Bot

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
BOT_TOKEN = "7725944062:AAFf584dTC6czU5ugP0-v_3Y23ip9M2Y-qo"
CHAT_ID = "-1001279674881"  # Replace with your channel username or chat ID
BASE_URL = "https://www.baiscope.lk"

# Initialize the bot
bot = Bot(token=BOT_TOKEN)

def download_file(download_url, file_name):
    try:
        response = requests.get(download_url)
        response.raise_for_status()  # Raise an error for bad responses
        with open(file_name, 'wb') as file:
            file.write(response.content)
        logging.info(f"Downloaded {file_name}.")
    except requests.HTTPError as http_err:
        logging.error(f"HTTP error occurred while downloading {file_name}: {http_err}")
    except Exception as e:
        logging.error(f"An error occurred while downloading {file_name}: {e}")

def upload_to_telegram(file_path):
    try:
        with open(file_path, "rb") as f:
            response = bot.send_document(chat_id=CHAT_ID, document=f)
            logging.info(f"Uploaded {file_path} to Telegram. Response: {response}")
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}. Unable to upload to Telegram.")
    except Exception as e:
        logging.error(f"Failed to upload {file_path} to Telegram (Error: {e})")

def fetch_download_links(subcategory_url):
    download_links = []
    try:
        response = requests.get(subcategory_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all download links on the subcategory page
        for link in soup.find_all('a', class_='dlm-buttons-button'):
            if 'href' in link.attrs:
                download_links.append(link['href'])
    except Exception as e:
        logging.error(f"Failed to fetch download links from {subcategory_url} (Error: {e})")
    return download_links

def process_subcategory(subcategory_url):
    logging.info(f"Processing subcategory URL: {subcategory_url}")
    download_links = fetch_download_links(subcategory_url)
    
    if not download_links:
        logging.warning("No download links found.")
        return

    for download_link in download_links:
        file_name = download_link.split("/")[-1] + ".zip"  # Assuming the filename should be the last part of the URL
        logging.info(f"Processing download link: {download_link}")
        download_file(download_link, file_name)
        upload_to_telegram(file_name)

def main():
    while True:
        logging.info("Starting download and upload cycle.")
        # Example subcategory URL
        subcategory_url = f"{BASE_URL}/berserk-2016-2017-s02-e01-e02-sinhala-subtitles/"
        process_subcategory(subcategory_url)
        
        logging.info("Waiting for the next cycle...")
        time.sleep(60)  # Wait for 60 seconds before the next cycle

if __name__ == "__main__":
    main()
