from googleapiclient.discovery import build
import isodate
from datetime import datetime


#Using YouTube API to Extract More Details 
                
# YouTube Data API setup
api_key = "AIzaSyAZvgYq31O_Pfv3a2-3do9plUyHTQypFD8"  
youtube = build("youtube", "v3", developerKey=api_key)


#Function to Get Video Details
def get_video_details(video_id):
    try:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        response = request.execute()
        
        if "items" in response and len(response["items"]) > 0:
            video = response["items"][0]
            #title = video["snippet"]["title"]
            #creator_name = video["snippet"]["channelTitle"]
            thumbnail = video["snippet"]["thumbnails"]["high"]["url"]
            description = video["snippet"]["description"]
            #views = video["statistics"].get("viewCount", "N/A")
            likes = video["statistics"].get("likeCount", "N/A")
            
            # Convert published date to "Date Month Year" format
            published_on = convert_published_date(video["snippet"]["publishedAt"])
            
            """
            # Extract duration in ISO 8601 format (e.g., "PT1H2M3S")
            duration_iso = video["contentDetails"]["duration"]
            duration = convert_iso_duration(duration_iso)
            """

            #return title, creator_name, description, thumbnail, views, likes, duration, published_on
            return description, thumbnail, format_number(likes), published_on
    except Exception as e:
        print(f"Error retrieving video details: {e}")
    #return None, None, None, None, None, None, None, None
    return None, None, None, None





#Function to Get Playlist Details
def get_playlist_details(playlist_id):
    try:
        request = youtube.playlists().list(
            part="snippet,contentDetails",
            id=playlist_id
        )
        response = request.execute()
        
        if "items" in response and len(response["items"]) > 0:
            playlist = response["items"][0]
            #title = playlist["snippet"]["title"]
            #creator_name = playlist["snippet"]["channelTitle"]
            thumbnail = playlist["snippet"]["thumbnails"]["high"]["url"]
            description = playlist["snippet"]["description"]
            
            # Convert published date to "Date Month Year" format
            published_on = convert_published_date(playlist["snippet"]["publishedAt"])

            # Calculate the total duration by fetching video details within the playlist
            #total_duration = calculate_total_playlist_duration(playlist_id)

            # Get the total view count using a separate function
            #view_count = get_playlist_views(playlist_id)

            # Estimate total views and likes using the first 10 videos
            aviews, alikes = estimate_playlist_popularity(playlist_id)
            
            #return title, creator_name, description, thumbnail, view_count, total_duration, published_on
            return description, thumbnail, aviews, alikes, published_on
    except Exception as e:
        print(f"Error retrieving playlist details: {e}")
    return None, None, None, None, None



#Helper Functions 

#Finding the Estimated Views & Likes of Playlist
# youtube_api.py

def estimate_playlist_popularity(playlist_id):
    total_views = 0
    total_likes = 0
    avg_views = 0
    avg_likes = 0
    videos_processed = 0  # Counter to keep track of the number of videos processed
    max_videos = 10  # Limit to the first 10 videos

    try:
        while True:
            request = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id,
                maxResults=10,
            )
            response = request.execute()
            
            video_ids = [item["contentDetails"]["videoId"] for item in response["items"]]
            for vid in video_ids:
                
                if videos_processed >= max_videos:
                    break  # Exit the loop if we've processed enough videos

                if video_ids:
                    video_ids_str = ','.join(video_ids)
                    total_views, total_likes = get__combined_play_video_details(video_ids_str)
                
                """
                # Check if views and likes contain commas and convert if necessary
                if isinstance(views, str) and ',' in views:
                    views = int(views.replace(',', ''))
                else:
                    views = int(views)
                total_views += views

                if isinstance(likes, str) and ',' in likes:
                    likes = int(likes.replace(',', ''))
                else:
                    likes = int(likes)
                total_likes += likes
                """

                videos_processed += 1  # Increment the counter for each processed video

            if videos_processed >= max_videos:
                break  # Exit the loop if we've processed enough videos or there are no more pages
            
        avg_views = round(total_views / 10)
        avg_likes = round(total_likes / 10)
        

        return format_number(avg_views), format_number(avg_likes) 
    except Exception as e:
        print(f"Error estimating playlist popularity: {e}")
        return "N/A", "N/A"



def get__combined_play_video_details(vid):
    total_views = 0
    total_likes = 0
    try:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=vid
        )
        response = request.execute()
        
        for video in response["items"]:
            views = video["statistics"].get("viewCount", "0")
            likes = video["statistics"].get("likeCount", "0")

            # Check if views and likes contain commas and convert if necessary
            if isinstance(views, str) and ',' in views:
                views = int(views.replace(',', ''))
            else:
                views = int(views)
            total_views += views

            if isinstance(likes, str) and ',' in likes:
                likes = int(likes.replace(',', ''))
            else:
                likes = int(likes)
            total_likes += likes

        """
        if "items" in response and len(response["items"]) > 0:
            video = response["items"][0]
    
            views = video["statistics"].get("viewCount", "N/A")
            print(views)
            likes = video["statistics"].get("likeCount", "N/A")
            print(likes)
        """
            

        #return views, likes
        return total_views, total_likes 
    except Exception as e:
        print(f"Error retrieving video details: {e}")
    return None, None



"""
# Function to batch process video details (up to 50 IDs per request)
def get_estplay_vid_details(video_ids):
    try:
        video_ids_str = ",".join(video_ids)
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_ids_str
        )
        response = request.execute()

        video_details = {}
        if "items" in response:
            for video in response["items"]:
                video_id = video["id"]
                #title = video["snippet"]["title"]
                #creator_name = video["snippet"]["channelTitle"]
                #thumbnail = video["snippet"]["thumbnails"]["high"]["url"]
                #description = video["snippet"]["description"]
                views = format_number(video["statistics"].get("viewCount", "0"))
                likes = format_number(video["statistics"].get("likeCount", "0"))
                #published_on = convert_published_date(video["snippet"]["publishedAt"])
                #duration_iso = video["contentDetails"]["duration"]
                #duration = convert_iso_duration(duration_iso)

                video_details[video_id] = {
                    #"title": title,
                    #"creator_name": creator_name,
                    #"thumbnail": thumbnail,
                    #"description": description,
                    "views": views,
                    "likes": likes,
                    #"duration": duration,
                    #"published_on": published_on
                }
        return video_details
    except Exception as e:
        print(f"Error retrieving batch video details: {e}")
        return {}
"""




#Convert ISO Published On to Date Month Year Format 
def convert_published_date(published_at):
    try:
        # Convert ISO 8601 string to datetime object
        date_obj = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
        # Format it to "Day Month Year" format (e.g., 25 Sep 2022)
        formatted_date = date_obj.strftime("%d %b %Y")
        return formatted_date
    except Exception as e:
        print(f"Error converting published date: {e}")
        return "N/A"





#Converting Views & Likes to More Reradable Format 
def format_number(number):
    try:
        num = int(number)
        if num >= 1_000_000:
            return f"{round(num / 1_000_000, 1)}M"
        elif num >= 1_000:
            return f"{round(num / 1_000, 1)}K"
        else:
            return str(num)
    except Exception as e:
        print(f"Error formatting number: {e}")
        return number  # Return the original if there's an error





def extract_video_id(url):
                    # Extract the video ID from the URL
                    if "watch?v=" in url:
                        return url.split("watch?v=")[1].split("&")[0]
                    return None



def extract_playlist_id(url):
    # Extract the playlist ID from the URL
    if "list=" in url:
        return url.split("list=")[1].split("&")[0]
    return None





"""
#Converting Duration
def convert_iso_duration(iso_duration):
    try:
        duration_hr = isodate.parse_duration(iso_duration)
        hours = duration_hr.total_seconds() // 3600
        minutes = (duration_hr.total_seconds() % 3600) // 60
        return f"{int(hours)}h {int(minutes)}m" if hours > 0 else f"{int(minutes)}m"
    except Exception as e:
        print(f"Error converting duration: {e}")
        return "N/A"
"""

"""
#Total Duration of Playlist
def calculate_total_playlist_duration(playlist_id):
    total_seconds = 0
    next_page_token = None
    
    while True:
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        
        video_ids = [item["contentDetails"]["videoId"] for item in response["items"]]
        
        for video_id in video_ids:
            video_duration = get_video_details(video_id)[6]  # Duration is the 6th element in the returned tuple
            if video_duration and "m" in video_duration:
                parts = video_duration.split("h ")
                if len(parts) == 2:
                    total_seconds += int(parts[0]) * 3600 + int(parts[1].replace("m", "")) * 60
                else:
                    total_seconds += int(parts[0].replace("m", "")) * 60
        
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    
    return f"{total_seconds // 3600}h {total_seconds % 3600 // 60}m"
"""
