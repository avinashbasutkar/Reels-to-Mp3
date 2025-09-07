# This version will do the following:
# uses RapidAPI to fetch the MP4 URL of Instagram Reels.
# passes the mp4 URL to Free Convert API for conversion to MP3.

import requests
import time
from datetime import datetime

start_time = datetime.now()  # Start timer to track script execution time

# Read Bearer token from .env file
def get_creds(env_path, var_name):
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith(var_name + "="):
                return line.strip().split("=", 1)[1]
    return None

env_path = r"D:\Reels to Mp3\.env"
bearer_token = get_creds(env_path, "mp4-to-mp3-convert")
x_rapidapi_key = get_creds(env_path, "x-rapidapi-key")
x_rapidapi_host = get_creds(env_path, "x-rapidapi-host")
soundcloud_client_id = get_creds(env_path, "soundcloud_client_id")
soundcloud_client_secret = get_creds(env_path, "soundcloud_client_secret")
soundcloud_redirect_uri = get_creds(env_path, "soundcloud_redirect_uri")
soundcloud_code_verifier = get_creds(env_path, "soundcloud_code_verifier")
soundcloud_code = get_creds(env_path, "soundcloud_code")  # Get this fromt the browser

# Read and extract Reel IDs from reels_urls.txt
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

# url = "https://instagram362.p.rapidapi.com/post/C0bs0fyPfuu"

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

    if mp4_url and bearer_token:
        fc_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {bearer_token}'
        }
        retry = True
        while retry:
            # Step 1: Import URL
            r = requests.post(
                'https://api.freeconvert.com/v1/process/import/url',
                headers=fc_headers,
                json={"url": mp4_url}
            )
            fc_response = r.json()
            task_id = fc_response.get("id")
            print(f"Import URL task_id: {task_id}")

            # Poll until status is 'completed'
            while True:
                r = requests.get(f'https://api.freeconvert.com/v1/process/tasks/{task_id}', headers=fc_headers)
                status_response = r.json()
                print(status_response.get("status"))
                status = status_response.get("status")
                if status == "completed":
                    print("Import URL Task completed!")
                    break
                elif status == "failed":
                    print("Import URL Task failed.")
                    break
                time.sleep(5)

            if status != "completed":
                print("Retrying import step...")
                continue  # Restart from import step

            # Step 2: Convert
            r = requests.post('https://api.freeconvert.com/v1/process/convert', 
                            headers=fc_headers,
                            json={
                                "input": f"{task_id}",
                                "input_format": "mp4",
                                "output_format": "mp3"
                            })
            convert_task_response = r.json()
            convert_task_id = convert_task_response.get("id")
            print(f"Convert task_id: {convert_task_id}")

            # Step 3: Export
            r = requests.post('https://api.freeconvert.com/v1/process/export/url', 
                            headers=fc_headers,
                            json={
                                "input": f"{convert_task_id}"
                            })
            export_response = r.json()
            export_task_id = export_response.get("id")

            # Poll until status is 'completed'
            while True:
                r = requests.get(f'https://api.freeconvert.com/v1/process/tasks/{export_task_id}', headers=fc_headers)
                status_response = r.json()
                print(status_response.get("status"))
                status = status_response.get("status")
                if status == "completed":
                    print("Export Task completed!")
                    mp3_url = status_response.get("result", {}).get("url")
                    if mp3_url:
                        print(f"MP3 Download URL: {mp3_url}")
                        mp3_response = requests.get(mp3_url)
                        mp3_content = mp3_response.content  # Hold MP3 content in variable
                        print("MP3 content fetched and held in memory.")
                    else:
                        print("MP3 URL not found in result.")
                    retry = False  # Success, exit loop
                    break
                elif status == "failed":
                    print("Export Task failed. Restarting from import step...")
                    break  # Will restart from import step
                time.sleep(5)
    else:
        print("Missing MP4 URL or Bearer token.")

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
    else:
        print("Missing SoundCloud OAuth credentials or code.")

    # Step 3: Upload MP3 to SoundCloud
    if access_token and mp3_content:
        upload_url = "https://api.soundcloud.com/tracks"
        upload_headers = {
            "accept": "application/json; charset=utf-8",
            "Authorization": f"OAuth {access_token}"
        }
        files = {
            "track[title]": (None, reel_id),  # Use reel_id as title
            "track[asset_data]": ("output.mp3", mp3_content, "audio/mpeg")
        }
        r = requests.post(upload_url, headers=upload_headers, files=files)
        upload_response = r.json()
        print("SoundCloud upload response:", upload_response)
        # Grab track id from upload response
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