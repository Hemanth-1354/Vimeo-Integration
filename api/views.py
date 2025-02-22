import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
import vimeo
import os 
import json



VIMEO_API_URL = "https://api.vimeo.com"

def home(request):
    return render(request, 'home.html')


def vimeo_request(method, endpoint, data=None, files=None):
    headers = {
        "Authorization": f"Bearer {settings.VIMEO_ACCESS_TOKEN}",
    }
    url = f"{VIMEO_API_URL}{endpoint}"

    try:
        if method == "POST" and files:
            del headers["Content-Type"]
            response = requests.post(url, headers=headers, data=data, files=files)
        else:
            headers["Content-Type"] = "application/json"
            response = requests.request(method, url, headers=headers, json=data)

        try:
            response_data = response.json()
        except ValueError:
            response_data = {"error": "Invalid JSON response from Vimeo API"}

        if response.status_code >= 400:
            return {"error": response_data.get("error", "Unknown error"), "status_code": response.status_code}

        return response_data

    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}", "status_code": 500}


def search_videos(request):
    query = request.GET.get('query', '')
    if query:
        endpoint = f"/videos?query={query}&page=1&per_page=10"
        response = vimeo_request("GET", endpoint)

        if "error" in response:
            return JsonResponse(response, status=response.get("status_code", 500))

        video_titles = [video.get("name") for video in response.get("data", [])]
        return JsonResponse({"titles": video_titles})
    return JsonResponse({"error": "No query provided"}, status=400)

def video_details(request, video_id):
    endpoint = f"/videos/{video_id}"
    details = vimeo_request("GET", endpoint)

    if "error" in details:
        return JsonResponse(details, status=details.get("status_code", 500))

    video_info = {
        "Name": details.get("name"),
        "Published Date": details.get("release_time"),
        "Channel": details.get("user", {}).get("name"),
        "Views": details.get("stats", {}).get("plays", "N/A"),
        "Video Link": details.get("link"),
        "Duration (seconds)": details.get("duration"),
        "Thumbnail": details.get("pictures", {}).get("base_link", "No thumbnail available")
    }

    return JsonResponse({"Video Details": video_info}, json_dumps_params={"indent": 4})

def embed_video(request, video_id):
    endpoint = f"/videos/{video_id}"
    video = vimeo_request("GET", endpoint)

    if "error" in video:
        return JsonResponse(video, status=video.get("status_code", 500))

    embed_code = video.get("embed", {}).get("html", "Embed code not available")
    return JsonResponse({"embed_code": embed_code})

def channel_details(request, channel_id):
    endpoint = f"/channels/{channel_id}"
    response = vimeo_request("GET", endpoint)

    if "error" in response:
        return JsonResponse(response, status=response.get("status_code", 500))

    channel_info = {
        "name": response.get("name"),
        "description": response.get("description"),
        "link": response.get("link"),
        "owner": {
            "name": response.get("user", {}).get("name"),
            "profile_link": response.get("user", {}).get("link"),
            "location": response.get("user", {}).get("location"),
            "profile_picture": response.get("user", {}).get("pictures", {}).get("base_link", "No profile picture available")
        },
        "total_videos": response.get("metadata", {}).get("connections", {}).get("videos", {}).get("total", 0)
    }
    return JsonResponse(channel_info)





from django.views.decorators.csrf import csrf_exempt


# Function to get headers for Vimeo API requests
def get_headers():
    return {
        "Authorization": f"Bearer {settings.VIMEO_ACCESS_TOKEN}",
        "Accept": "application/vnd.vimeo.*+json;version=3.4",
        "Content-Type": "application/json"
    }

# Initialize Vimeo Client
client = vimeo.VimeoClient(
    token=settings.VIMEO_ACCESS_TOKEN,
    key=settings.VIMEO_CLIENT_ID,
    secret=settings.VIMEO_CLIENT_SECRET
)





@csrf_exempt
def upload_video(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        video_path = data.get("video_path")

        if not video_path or not os.path.exists(video_path):
            return JsonResponse({"error": "Invalid file path or file does not exist"}, status=400)

        uri = client.upload(video_path, data={
            'name': os.path.basename(video_path),
            'description': 'Uploaded via API'
        })

        return JsonResponse({
            "success": True,
            "video_uri": uri,
            "video_link": f"https://vimeo.com/manage/{uri}"
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except vimeo.exceptions.VimeoUploadFailure as e:
        return JsonResponse({"error": f"Upload failed: {str(e)}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)



@csrf_exempt
def edit_video(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        video_id = data.get("video_id")
        title = data.get("title")
        description = data.get("description")

        if not video_id:
            return JsonResponse({"error": "Video ID is required"}, status=400)

        update_data = {"name": title, "description": description}
        
        # Update video details
        client.patch(f"/videos/{video_id}", data=update_data)


        return JsonResponse({"success": True, "message": "Video updated successfully"})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)
