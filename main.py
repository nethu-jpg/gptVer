import requests
from bs4 import BeautifulSoup
import os
import logging
import aiohttp
import asyncio

# Constants
BOT_TOKEN = "7725944062:AAFf584dTC6czU5ugP0-v_3Y23ip9M2Y-qo"
CHAT_ID = "-1001279674881"  # Replace with your channel username or chat ID
BASE_URL = "https://www.baiscope.lk"
DOWNLOAD_DIR = "downloads"

# Set up logging
logging.basicConfig(level=logging.INFO)

async def send_document(session, file_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(file_path, 'rb') as file:
        data = {
            'chat_id': CHAT_ID,
            'document': file,
        }
        async with session.post(url, data=data) as response:
            if response.status == 200:
                logging.info(f"Uploaded {file_path} to Telegram.")
            else:
                logging.error(f"Failed to upload {file_path} to Telegram (Error: {response.text})")

def download_file(url, session):
    response = session.get(url)
    if response.status_code == 200:
        file_name = url.split("/")[-1] + ".zip"
        file_path = os.path.join(DOWNLOAD_DIR, file_name)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        logging.info(f"Downloaded {file_name}.")
        return file_path
    else:
        logging.error(f"Failed to download {url} (Error: {response.status_code}).")
        return None

def fetch_and_process_links():
    with requests.Session() as session:
        response = session.get(BASE_URL)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all subcategory links
        subcategory_links = soup.find_all('a', href=True)

        for link in subcategory_links:
            subcategory_url = link['href']
            logging.info(f"Processing subcategory URL: {subcategory_url}")
            response = session.get(subcategory_url)
            sub_soup = BeautifulSoup(response.content, 'html.parser')

            # Find download links
            download_links = sub_soup.find_all('a', href=True)

            for download_link in download_links:
                download_url = download_link['href']
                logging.info(f"Processing download link: {download_url}")

                file_path = download_file(download_url, session)
                if file_path:
                    asyncio.run(send_document(aiohttp.ClientSession(), file_path))

def main():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    while True:
        try:
            fetch_and_process_links()
            logging.info("Waiting for the next cycle...")
            asyncio.sleep(60)  # Wait for a minute before the next cycle
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    main()
