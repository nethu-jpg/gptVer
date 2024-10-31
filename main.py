import requests
from bs4 import BeautifulSoup
from telegram import Bot
import os
import time
import logging

# Telegram Bot Token and Channel Chat ID from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Telegram bot setup
bot = Bot(token=BOT_TOKEN)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_subcategory_links():
    url = "https://www.baiscope.lk"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching the main page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")

    # Find links to individual categories or series
    subcategory_links = [
        link["href"] for link in soup.find_all("a", href=True)
        if "berserk" in link["href"]  # Modify this condition based on what you want to fetch
    ]

    if subcategory_links:
        logging.info(f"Found {len(subcategory_links)} subcategory link(s).")
    else:
        logging.warning("No subcategory links found.")

    return subcategory_links

def get_download_links(subcategory_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    try:
        response = requests.get(subcategory_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching the subcategory page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")

    # Find the download links in the subcategory page
    download_links = [
        link["href"] for link in soup.find_all("a", class_="dlm-buttons-button-baiscopebutton", href=True)
    ]

    if download_links:
        logging.info(f"Found {len(download_links)} download link(s) in {subcategory_url}.")
    else:
        logging.warning(f"No download links found in {subcategory_url}.")

    return download_links

def download_file(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Extract file name from URL or use a default name
        file_name = url.split("/")[-2] + ".zip"
        file_path = os.path.join("downloads", file_name)
        
        os.makedirs("downloads", exist_ok=True)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        logging.info(f"Downloaded {file_name}")
        return file_path

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download {url} (Error: {e})")
        return None

def upload_to_telegram(file_path):
    try:
        with open(file_path, "rb") as f:
            bot.send_document(chat_id=CHAT_ID, document=f)
        logging.info(f"Uploaded {file_path} to Telegram.")
    except Exception as e:
        logging.error(f"Failed to upload {file_path} to Telegram (Error: {e})")

def run_cycle():
    logging.info("Starting download and upload cycle.")
    
    # Step 1: Get subcategory links
    subcategory_links = get_subcategory_links()
    
    for subcategory_url in subcategory_links:
        logging.info(f"Processing subcategory URL: {subcategory_url}")
        
        # Step 2: Get download links from each subcategory
        download_links = get_download_links(subcategory_url)
        
        if not download_links:
            logging.warning(f"No download links to process from {subcategory_url}.")
            continue
        
        for link in download_links:
            full_url = link if link.startswith("http") else "https://www.baiscope.lk" + link
            logging.info(f"Processing download link: {full_url}")
            
            file_path = download_file(full_url)
            if file_path:
                upload_to_telegram(file_path)
                os.remove(file_path)  # Clean up after sending
            else:
                logging.error(f"Skipping failed download: {full_url}")

    logging.info("Cycle completed. Waiting for the next cycle...")

if __name__ == "__main__":
    while True:
        run_cycle()
        time.sleep(10)  # Wait 1 hour before next cycle
