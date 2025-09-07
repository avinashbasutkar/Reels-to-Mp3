# Instagram Reels to SoundCloud MP3 Uploader

This project automates the process of downloading Instagram Reels videos, converting them to MP3 audio, and uploading them to SoundCloud using the SoundCloud API.

## Features

- Fetches Instagram Reel video URLs using RapidAPI.
- Downloads MP4 videos locally.
- Converts MP4 videos to MP3 audio using `moviepy`.
- Uploads MP3 tracks to SoundCloud with unique titles.
- Manages SoundCloud OAuth tokens (access & refresh tokens) for seamless uploads.
- Tracks script run time.

## Requirements

- Python 3.8+
- [moviepy](https://github.com/Zulko/moviepy)
- [requests](https://docs.python-requests.org/en/latest/)

Install dependencies:
```sh
pip install -r requirements.txt
```

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/Reels-to-Mp3.git
   ```

2. **Create a `.env` file** in the project root with your credentials:
   ```
   x-rapidapi-key=YOUR_RAPIDAPI_KEY
   x-rapidapi-host=YOUR_RAPIDAPI_HOST
   soundcloud_client_id=YOUR_SOUNDCLOUD_CLIENT_ID
   soundcloud_client_secret=YOUR_SOUNDCLOUD_CLIENT_SECRET
   soundcloud_redirect_uri=YOUR_SOUNDCLOUD_REDIRECT_URI
   soundcloud_code_verifier=YOUR_PKCE_CODE_VERIFIER
   soundcloud_code=YOUR_SOUNDCLOUD_AUTHORIZATION_CODE
   ```

3. **Add Instagram Reel URLs**  
   Put your Instagram Reel URLs in `files/reels_urls.txt`, one per line.

4. **Run the script:**
   ```sh
   python python scripts/main_v4.py
   ```

## Notes

- The script will save and reuse SoundCloud access/refresh tokens in `soundcloud_tokens.json`.
- Temporary MP4/MP3 files are created for conversion and can be deleted after upload.
- Do **not** commit your `.env` or token files to GitHub.

## Author

Avinash Basutkar (https://github.com/avinashbasutkar)