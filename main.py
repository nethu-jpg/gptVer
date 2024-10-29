import requests
from bs4 import BeautifulSoup
import os
import telegram

# Initialize Telegram bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telegram.Bot(token=BOT_TOKEN)

# Function to download files
def download_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for bad responses
        filename = url.split('/')[-2] + '.zip'  # Change file extension if needed
        with open(f'downloads/{filename}', 'wb') as f:
            f.write(response.content)
        return filename
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

# Function to upload files to Telegram
def upload_to_telegram(file_path):
    with open(file_path, 'rb') as f:
        bot.send_document(chat_id=CHAT_ID, document=f)

# Function to scrape the webpage for download links
def scrape_links():
    url = "https://www.baiscope.lk/"  # Change to the target page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all links with specific class
    links = soup.find_all('a', class_='dlm-buttons-button-baiscopebutton')
    
    for link in links:
        download_url = link.get('href')  # Extract the URL
        if download_url:
            full_url = f"https://www.baiscope.lk{download_url}"  # Complete the URL
            print(f"Downloading from {full_url}...")
            file_name = download_file(full_url)
            if file_name:
                print(f"Uploading {file_name} to Telegram...")
                upload_to_telegram(f'downloads/{file_name}')
            else:
                print("Download failed.")

if __name__ == "__main__":
    os.makedirs('downloads', exist_ok=True)  # Create a directory for downloads
    scrape_links()
