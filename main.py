import requests
import os
from telegram import Bot
from telegram.error import TelegramError
import time

# Telegram Bot setup
BOT_TOKEN = "7725944062:AAFf584dTC6czU5ugP0-v_3Y23ip9M2Y-qo"  # Replace with your bot token
CHAT_ID = "-1001279674881"               # Replace with your chat ID
bot = Bot(token=BOT_TOKEN)

# Base URL setup for downloading files
BASE_URL = "https://www.baiscope.lk/Downloads/"
START_ID = 80390   # The first file ID you want to start from
END_ID = 80400     # Adjust to the number of files you need
OUTPUT_FOLDER = "downloads"

# Create downloads folder if it doesn't exist
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def download_file(file_id):
    url = f"{BASE_URL}{file_id}/"
    try:
        print(f"Downloading from {url}...")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            file_name = f"{OUTPUT_FOLDER}/{file_id}.zip"  # Modify based on file type if known
            with open(file_name, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Downloaded {file_name}")
            return file_name
        else:
            print(f"Failed to download {url} (Status Code: {response.status_code})")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return None

def send_to_telegram(file_path):
    try:
        print(f"Uploading {file_path} to Telegram...")
        with open(file_path, 'rb') as file:
            bot.send_document(chat_id=CHAT_ID, document=file)
        print(f"Uploaded {file_path} successfully!")
    except TelegramError as e:
        print(f"Failed to upload {file_path} to Telegram: {e}")

# Main loop to download and upload
for file_id in range(START_ID, END_ID + 1):
    file_path = download_file(file_id)
    if file_path:
        send_to_telegram(file_path)
        time.sleep(2)  # Add delay to respect API rate limits
