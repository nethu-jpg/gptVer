import os
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# Initialize Telegram bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

print("Bot starting...")
print("Token:", BOT_TOKEN)  # Check if BOT_TOKEN is being loaded correctly

# Add more print statements to see if other parts of the code are running
# e.g., after fetching a link, starting a download, etc.


# Function to get download links
def get_download_links():
    url = "https://www.baiscope.lk"  # Main URL where links are listed
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all <a> tags with 'Downloads' in the href attribute
    links = []
    for a_tag in soup.find_all('a', href=True):
        if '/Downloads/' in a_tag['href']:
            full_url = url + a_tag['href']
            links.append(full_url)
    return links

# Function to download and upload file
def download_and_upload_file(link):
    try:
        # Download the file
        response = requests.get(link)
        if response.status_code == 200:
            filename = link.split("/")[-2] + ".file"  # Extract filename from link
            with open(filename, "wb") as file:
                file.write(response.content)
            
            # Upload to Telegram
            with open(filename, "rb") as file:
                bot.send_document(chat_id=CHAT_ID, document=file)
            print(f"Uploaded {filename} successfully!")
            
            # Clean up
            os.remove(filename)
        else:
            print(f"Failed to download {link} (Status Code: {response.status_code})")
    except Exception as e:
        print(f"Error processing {link}: {e}")

# Main loop to check for new links
processed_links = set()  # To keep track of already processed links
while True:
    links = get_download_links()
    for link in links:
        if link not in processed_links:
            download_and_upload_file(link)
            processed_links.add(link)
    
    # Wait before checking again
    time.sleep(20)  # Check every 5 minutes
