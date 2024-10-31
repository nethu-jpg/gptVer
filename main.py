import os
import time
import requests
from telegram import Bot, InputFile
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import logging

# Initialize Telegram bot with your Bot Token and Channel Chat ID
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Base URL of the website to scrape
BASE_URL = "https://www.baiscope.lk"

# Folder to store downloaded files
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Function to fetch download URLs from the site
def fetch_download_links():
    try:
        logging.info(f"Fetching download page: {BASE_URL}")
        response = requests.get(BASE_URL)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        links = []
        
        # Find all download links matching the specified criteria
        for link in soup.find_all('a', href=True, class_="dlm-buttons-button"):
            url = link['href']
            if "/Downloads/" in url:
                full_url = BASE_URL + url
                links.append(full_url)
                logging.info(f"Found download link: {full_url}")
        
        if not links:
            logging.warning("No download links found.")
        
        return links

    except RequestException as e:
        logging.error(f"Error fetching download links: {e}")
        return []

# Function to download and save the file
def download_file(url):
    try:
        logging.info(f"Attempting to download from {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Create a unique filename for each download
        file_id = url.split("/")[-2]
        file_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.zip")

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        logging.info(f"Downloaded {file_path}")
        return file_path

    except RequestException as e:
        logging.error(f"Failed to download {url}: {e}")
        return None

# Function to upload the file to the Telegram channel
def upload_to_telegram(file_path):
    try:
        logging.info(f"Uploading {file_path} to Telegram...")
        with open(file_path, 'rb') as file:
            bot.send_document(chat_id=CHAT_ID, document=InputFile(file, filename=os.path.basename(file_path)))
        logging.info(f"Uploaded {file_path} successfully!")

    except Exception as e:
        logging.error(f"Failed to upload {file_path} to Telegram: {e}")

# Main function to run the download-upload cycle
def download_and_upload_cycle():
    logging.info("Starting download and upload cycle.")
    download_links = fetch_download_links()

    if not download_links:
        logging.warning("No download links to process.")
        return

    for url in download_links:
        file_path = download_file(url)
        if file_path:
            upload_to_telegram(file_path)
            os.remove(file_path)
            logging.info(f"Deleted local file: {file_path}")
        else:
            logging.warning(f"Skipping upload for {url} due to download error.")

# Loop to repeat the cycle at a set interval
while True:
    download_and_upload_cycle()
    logging.info("Waiting for the next cycle...")
    time.sleep(30)  # Run every hour
