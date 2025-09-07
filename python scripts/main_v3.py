# This version uses moviepy to convert MP4 to MP3 locally instead of using Free Convert API.

import requests
import time
from datetime import datetime
from moviepy import VideoFileClip
import io

start_time = datetime.now()  # Start timer to track script execution time

def get_creds(env_path, var_name):
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith(var_name + "="):
                return line.strip().split("=", 1)[1]
    return None

env_path = r"D:\Reels to Mp3\.env"
x_rapidapi_key = get_creds(env_path, "x-rapidapi-key")
x_rapidapi_host = get_creds(env_path, "x-rapidapi-host")
soundcloud_client_id = get_creds(env_path, "soundcloud_client_id")
soundcloud_client_secret = get_creds(env_path, "soundcloud_client_secret")
soundcloud_redirect_uri = get_creds(env_path, "soundcloud_redirect_uri")
soundcloud_code_verifier = get_creds(env_path, "soundcloud_code_verifier")
soundcloud_code = get_creds(env_path, "soundcloud_code")  # Get this from the browser

urls_path = r"D:\Reels to Mp3\files\reels_urls.txt"
with open(urls_path, "r") as f:
    lines = f.readlines()

reel_ids = []
for line in lines:
    line = line.strip()
    if "/p/" in line:
        parts = line.split("/p/")
        if len(parts) > 1:
            reel_id = parts[1].split("/")[0]
            reel_ids.append(reel_id)

for reel_id in reel_ids:
    print(f"Processing Reel ID: {reel_id}")
    url = f"https://instagram362.p.rapidapi.com/post/{reel_id}"

    headers = {
        "x-rapidapi-key": x_rapidapi_key,
        "x-rapidapi-host": x_rapidapi_host
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    # Capture the 'videoUrl' field from the first item in the list response
    if isinstance(data, list) and len(data) > 0 and 'videoUrl' in data[0]:
        mp4_url = data[0]['videoUrl']
        print("Fetched MP4 URL")
        print()
    else:
        print("Failed to get MP4 URL.")
        mp4_url = None

    mp3_content = None

    if mp4_url:
        # Download MP4
        mp4_filename = f"temp_{reel_id}.mp4"
        print("Downloading MP4...")
        with requests.get(mp4_url, stream=True) as r:
            r.raise_for_status()
            with open(mp4_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("MP4 downloaded.")

        # Convert MP4 to MP3 using moviepy
        mp3_filename = f"temp_{reel_id}.mp3"
        print("Converting MP4 to MP3...")
        clip = VideoFileClip(mp4_filename)
        clip.audio.write_audiofile(mp3_filename)
        clip.close()
        print("MP3 conversion complete.")

        # Read MP3 content into memory
        with open(mp3_filename, "rb") as f:
            mp3_content = f.read()
        print("MP3 content fetched and held in memory.")

    else:
        print("Missing MP4 URL.")

    # Step 2: Generate SoundCloud Access Token
    access_token = None
    if soundcloud_client_id and soundcloud_client_secret and soundcloud_redirect_uri and soundcloud_code_verifier and soundcloud_code:
        token_url = "https://secure.soundcloud.com/oauth/token"
        payload = {
            "grant_type": "authorization_code",
            "client_id": soundcloud_client_id,
            "client_secret": soundcloud_client_secret,
            "redirect_uri": soundcloud_redirect_uri,
            "code_verifier": soundcloud_code_verifier,
            "code": soundcloud_code
        }
        headers = {
            "accept": "application/json; charset=utf-8",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        r = requests.post(token_url, data=payload, headers=headers)
        token_response = r.json()
        access_token = token_response.get("access_token")
        if access_token:
            print("SoundCloud access token generated.")
        else:
            print("Failed to generate SoundCloud access token:", token_response)
            exit()  # Stop execution if token generation fails
    else:
        print("Missing SoundCloud OAuth credentials or code.")
        exit()

    # Step 3: Upload MP3 to SoundCloud
    if access_token and mp3_content:
        upload_url = "https://api.soundcloud.com/tracks"
        upload_headers = {
            "accept": "application/json; charset=utf-8",
            "Authorization": f"OAuth {access_token}"
        }
        # Use reel_id and timestamp for unique title
        from datetime import datetime
        track_title = f"Instagram Reel MP3 - {reel_id} - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        files = {
            "track[title]": (None, track_title),
            "track[asset_data]": ("output.mp3", mp3_content, "audio/mpeg")
        }
        r = requests.post(upload_url, headers=upload_headers, files=files)
        upload_response = r.json()
        print("SoundCloud upload response:", upload_response)
        track_id = upload_response.get("id")
        if track_id:
            print(f"Uploaded track ID: {track_id}")
        else:
            print("Track ID not found in upload response.")
    elif not mp3_content:
        print("No MP3 content to upload.")
    elif not access_token:
        print("No SoundCloud access token for upload.")
        exit()  # Stop execution if token generation fails

end_time = datetime.now()  # End timer
elapsed = end_time - start_time
print(f"\nScript run time: {elapsed}")