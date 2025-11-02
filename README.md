# Watch2Gether → YouTube Playlist Automator

This script extracts all YouTube videos from a Watch2Gether room and
automatically adds them to a new YouTube playlist using the YouTube Data
API v3. It uses Selenium to read the room contents and the Google API
client to create and populate your playlist.

## Features

-   Scrapes every YouTube link visible in a Watch2Gether room
-   Automatically creates a private YouTube playlist
-   Adds all extracted videos to the playlist
-   Stores authentication tokens locally (login only required once)
-   Supports optional persistence to avoid adding duplicates across runs

## Requirements

### 1. Python packages

    pip install selenium google-auth google-auth-oauthlib google-api-python-client

### 2. Browser + WebDriver

You need either:

-   Firefox + geckodriver
-   Chrome + chromedriver

Download the appropriate driver:

-   geckodriver: https://github.com/mozilla/geckodriver/releases
-   chromedriver: https://chromedriver.chromium.org/downloads

Set the driver path in the script:

    PATH = r"YOUR DRIVER PATH"

### 3. Google Cloud setup

1.  Go to Google Cloud Console\
    https://console.cloud.google.com/
2.  Create (or select) a project
3.  Enable **YouTube Data API v3**
4.  Go to **APIs & Services → Credentials**
5.  Create an **OAuth 2.0 Client ID** (Desktop Application)
6.  Download the `credentials.json` file
7.  Update the script with your credentials path:

```{=html}
<!-- -->
```
    CRED_PATH = r"YOUR CREDENTIALS PATH"

On the first run, you will be prompted to log in and authorize access to
your YouTube account.

## Usage

### 1. Insert your Watch2Gether room link

    room_url = "YOUR WATCH2GETHER ROOM URL"

### 2. Run the script

    python scriptname.py

### 3. Authenticate (first run only)

A browser window will open prompting you to:

-   Log in to your Google account
-   Grant access for YouTube playlist management

A `token.json` file will be created automatically for future sessions.

### 4. View your finished playlist

Once the script completes, it prints a link similar to:

    Playlist complete: https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID

## Customization


### Switching from Firefox to Chrome

Replace:

``` python
webdriver.Firefox(...)
```

with:

``` python
webdriver.Chrome(...)
```

And update your driver path to a `chromedriver` binary.

### Adjusting page load speed

Increase this value if your Watch2Gether room loads slowly:

``` python
time.sleep(5)
```

## Notes

-   Some Watch2Gether rooms may require manual button clicks (e.g.,
    cookie banner, join room)
-   API quota limits apply if adding many videos
-   Duplicate-checking support exists if you enable the processed videos
    file

## License

MIT License
