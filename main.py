import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import time

# Environment Variables for Heroku
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BASE_URL = "https://www.baiscope.lk"  # Base URL for site

bot = Bot(token=BOT_TOKEN)

# Function to get all download links from the main page
def get_download_links():
    url = f"{BASE_URL}/Downloads/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', class_='dlm-buttons-button-baiscopebutton')]
        return [BASE_URL + link for link in links]
    else:
        print(f"Failed to fetch the page (Status Code: {response.status_code})")
        return []

# Function to download and upload files to Telegram
def download_and_upload():
    links = get_download_links()
    for link in links:
        print(f"Processing {link}...")
        file_name = link.split('/')[-2] + ".zip"  # Modify if files are .rar sometimes
        file_path = f"downloads/{file_name}"
        
        # Download the file
        response = requests.get(link)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded {file_path}")

            # Upload to Telegram
            with open(file_path, "rb") as f:
                bot.send_document(chat_id=CHAT_ID, document=f)
            print(f"Uploaded {file_path} to Telegram")
            
            # Optionally, delete file after upload
            os.remove(file_path)
            print(f"Deleted {file_path}")
        else:
            print(f"Failed to download {link} (Status Code: {response.status_code})")
        time.sleep(2)  # Optional delay between downloads

# Main loop for Heroku
if __name__ == "__main__":
    while True:
        download_and_upload()
        print("Waiting for the next cycle...")
        time.sleep(3600)  # Run once every hour
