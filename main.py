from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import os
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# dont forget to install the required packages, geckodriver (or chromedriver) and have firefox (or chrome) installed
# also make sure to enable youtube data api v3 in your google cloud console and download the credentials.json file
# you might need to press some buttons manually, like "accept cookies" or "join room"
# as well as logging in to your google account when using the script for the first time (it might say the script is unsafe, just proceed)


# Selenium Setup
def setup_firefox_driver():
    # change every Firefox to chrome if using chrome
    firefox_options = Options()
    PATH = r'YOUR PATH'   # Update with your geckodriver path (or chromedriver for Chrome)
    service = Service(PATH)
    return webdriver.Firefox(service=service, options=firefox_options)

def extract_youtube_id(url):
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&?\n]+)',
        r'youtube\.com\/watch\?.*v=([^&?\n]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def extract_video(driver, url):
    driver.get(url)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[href*='youtube.com']"))
    )
    # increase wait time if you have a slow connection or the page takes longer to load
    time.sleep(5)  # wait for additional content to load, necessary for rooms with many videos
    videos = []
    selector = ".cursor-pointer.hover\\:underline"

    try:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        for element in elements:
            try:
                href = element.get_attribute('href')
                title = element.text.strip() or element.get_attribute('title') or element.get_attribute('aria-label') or ""
                if not href or 'youtube.com/watch' not in href:
                    continue
                video_id = extract_youtube_id(href)
                if video_id:
                    videos.append({
                        'video_id': video_id,
                        'title': title,
                        'url': href
                    })
                    print(f"Found: {title} - {video_id}")
            except Exception as e:
                print(f"Element processing error: {e}")
                continue
    except Exception as e:
        print(f"Error finding elements: {e}")

    return videos


# YouTube API Setup
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_youtube_service():

    CRED_PATH = r"YOUR PATH"  # change this to the path to your credentials.json file
    CLIENT_SECRET_FILE = os.getenv("YT_CREDENTIALS_PATH", CRED_PATH)
    TOKEN_FILE = "token.json"

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

def create_playlist(youtube, title="W2G Playlist", description="Playlist created from Watch2Gether videos with W2GScript by Cryotic"):         #you can change the playlist name and description here, or do it later on youtube
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": description},
            "status": {"privacyStatus": "private"}
        }
    )
    response = request.execute()
    print(f"Created playlist: {response['snippet']['title']} (ID: {response['id']})")
    return response['id']

def add_video_to_playlist(youtube, playlist_id, video_id):
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id}
            }
        }
    )
    response = request.execute()
    print(f"Added video: {video_id}")
    return response

# Persistence Functions if to many videos are to be added (YT API has quota limits)
def load_processed_ids(path="added_videos.txt"):
    if not os.path.exists(path):
        return set()
    with open(path, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_processed_id(video_id, path="added_videos.txt"):
    with open(path, "a") as f:
        f.write(video_id + "\n")

def load_playlist_id(path="playlist_id.txt"):
    return open(path).read().strip() if os.path.exists(path) else None

def save_playlist_id(pid, path="playlist_id.txt"):
    with open(path, "w") as f:
        f.write(pid)


# Main Function
def main():
    driver = setup_firefox_driver()
    try:
        room_url = "YOUR ROOM"  # Change to your Watch2Gether Room URL
        print("Extracting videos from Watch2Gether...")
        videos = extract_video(driver, room_url)
    except Exception as e:
        print(f"Error: {e}")
        videos = []
    finally:
        driver.quit()
        print("Browser closed")

    if not videos:
        print("No videos found.")
        return

    # Authenticate with YouTube
    youtube = get_youtube_service()

    # Create playlist or load existing
    playlist_id = load_playlist_id()

    if not playlist_id:
        playlist_id = create_playlist(youtube, "W2G Auto Playlist")
        save_playlist_id(playlist_id)
    else:
        print(f"Using existing playlist: {playlist_id}")

    # Load already processed video IDs
    processed = load_processed_ids()

    # Add each video
    for video in videos:
        vid = video['video_id']

        # Skip videos already added
        if vid in processed:
            print(f"Skipping (already added): {vid}")
            continue

        try:
            add_video_to_playlist(youtube, playlist_id, vid)
            save_processed_id(vid)
        except Exception as e:
            print(f"Failed to add {vid}: {e}")

    print(f"Playlist complete: https://www.youtube.com/playlist?list={playlist_id}")

if __name__ == "__main__":
    main()
