import requests
from django.conf import settings
from pathlib import Path
import os

VIMEO_API_URL = "https://api.vimeo.com"

def get_headers():
    return {
        "Authorization": f"Bearer {settings.VIMEO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }


def search_videos(query):
    response = requests.get(
        f"{VIMEO_API_URL}/videos", headers=get_headers(), params={"query": query}
    )

    if response.status_code == 200:
        data = response.json()
        video_list = []

        for video in data.get("data", []):  # Loop through all results
            video_details = {
                "title": video.get("name"),  # Video title
                "description": video.get("description"),  # Video description
                "video_link": video.get("link"),  # Public Vimeo link
                "duration": video.get("duration"),  # Video duration (in seconds)
                "thumbnail": video.get("pictures", {}).get("base_link"),  # Thumbnail image
                "embed_code": video.get("embed", {}).get("html", ""),  # Embed HTML code
            }
            video_list.append(video_details)

        return video_list

    return {"error": "Failed to fetch videos"}



VIMEO_API_URL = "https://api.vimeo.com"

def upload_video(video_path, title, description):
    file_size = Path(video_path).stat().st_size  # Get file size

    # Step 1: Request an upload link from Vimeo
    response = requests.post(
        f"{VIMEO_API_URL}/me/videos",
        headers=get_headers(),
        json={
            "name": title,
            "description": description,
            "upload": {"approach": "tus", "size": str(file_size)}
        }
    )

    if response.status_code != 201:
        return {"error": "Failed to get upload URL", "details": response.json()}

    upload_url = response.json().get("upload", {}).get("upload_link")
    video_id = response.json().get("uri").split("/")[-1]

    # Step 2: Upload the video file
    with open(video_path, "rb") as video_file:
        upload_response = requests.patch(
            upload_url,
            headers={"Tus-Resumable": "1.0.0", "Upload-Offset": "0"},
            data=video_file
        )

    if upload_response.status_code not in [204, 200]:
        return {"error": "Video upload failed", "details": upload_response.json()}

    return {"success": True, "vimeo_id": video_id, "video_link": f"https://vimeo.com/{video_id}"}

def get_video_details(video_id):
    response = requests.get(f"{VIMEO_API_URL}/videos/{video_id}", headers=get_headers())
    return response.json() if response.status_code == 200 else {"error": "Failed to fetch video details"}

def get_user_details():
    response = requests.get(f"{VIMEO_API_URL}/me", headers=get_headers())
    return response.json()

def get_channel_details(channel_id):
    response = requests.get(f"{VIMEO_API_URL}/channels/{channel_id}", headers=get_headers())
    return response.json()
