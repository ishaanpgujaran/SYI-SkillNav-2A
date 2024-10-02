import re
from datetime import datetime

# Convert text-based views/likes into numeric values
def convert_to_number(text):
    text = text.lower().strip()
    if 'K' in text:
        return int(float(text.replace('K', '')) * 1000)
    elif 'M' in text:
        return int(float(text.replace('M', '')) * 1000000)
    elif 'B' in text:
        return int(float(text.replace('B', '')) * 1000000000)
    else:
        #return int(re.sub(r'\D', '', text))  # Remove non-digit characters and convert to int
        # Remove non-digit characters
        number = re.sub(r'\D', '', text)
        # Check if the resulting string is empty
        if number == '':
            return 0
        return int(number)

# Convert duration text into hours (for consistency across platforms)
def convert_duration_to_hours(duration_str):
    if 'hour' in duration_str:
        return int(duration_str.split()[0])
    elif 'minute' in duration_str:
        return int(duration_str.split()[0]) / 60
    elif 'week' in duration_str:
        return int(duration_str.split()[0]) * 7 * 24  # Convert weeks to hours
    elif 'month' in duration_str:
        return int(duration_str.split()[0]) * 30 * 24  # Convert months to hours
    else:
        return 0  # Handle 'N/A' or undefined durations

# Convert the published date to a comparable format
def calculate_date_score(published_on):
    if published_on == "Up to date":
        return 60  # Lower value for "Up to date"
    try:
        date_obj = datetime.strptime(published_on, "%d/%m/%y")
        days_since_published = (datetime.now() - date_obj).days
        return max(100 - (days_since_published / 365) * 100, 0)  # Score based on recency
    except Exception as e:
        return 0  # Return 0 if unable to parse the date


def get_max_values(cursor):
    # Get max values for YouTube Videos
    cursor.execute("SELECT MAX(CAST(views AS INTEGER)), MAX(CAST(likes AS INTEGER)), MAX(CAST(duration AS INTEGER)) FROM resources WHERE platform = 'YouTube' AND type = 'Video'")
    max_video_views, max_video_likes, max_video_duration = cursor.fetchone()

    # Get max values for YouTube Playlists (views, likes are averages)
    cursor.execute("SELECT MAX(CAST(views AS INTEGER)), MAX(CAST(likes AS INTEGER)), MAX(CAST(duration AS INTEGER)) FROM resources WHERE platform = 'YouTube' AND type = 'Playlist'")
    max_playlist_views, max_playlist_likes, max_playlist_duration = cursor.fetchone()

    # Get max values for Courses (Coursera + Class Central) for reviews (likes) and duration
    cursor.execute("SELECT MAX(CAST(likes AS INTEGER)), MAX(CAST(duration AS INTEGER)) FROM resources WHERE platform IN ('Coursera', 'Class Central')")
    max_course_reviews, max_course_duration = cursor.fetchone()

    return {
        'max_video_views': max_video_views or 1,
        'max_video_likes': max_video_likes or 1,
        'max_video_duration': max_video_duration or 1,
        'max_playlist_views': max_playlist_views or 1,
        'max_playlist_likes': max_playlist_likes or 1,
        'max_playlist_duration': max_playlist_duration or 1,
        'max_course_reviews': max_course_reviews or 1,
        'max_course_duration': max_course_duration or 1
    }


def normalize_resource(resource, max_values):
    # Unpack resource fields
    #resource_id, title, platform, type, views, likes, duration, published_on = resource
    resource_id, category, title, creator, platform, type, duration, views, likes, published_on, description, link, thumbnail, difficulty = resource


    # Initialize scores
    views_score = 0
    likes_score = 0
    duration_score = 0

    # Normalize values based on type
    if platform == "YouTube" and type == "Video":
        views_score = normalize(convert_to_number(views), max_values['max_video_views'])
        likes_score = normalize(convert_to_number(likes), max_values['max_video_likes'])
        duration_score = normalize(convert_duration_to_hours(duration), max_values['max_video_duration'])

    elif platform == "YouTube" and type == "Playlist":
        views_score = normalize(convert_to_number(views), max_values['max_playlist_views'])
        likes_score = normalize(convert_to_number(likes), max_values['max_playlist_likes'])
        duration_score = normalize(convert_duration_to_hours(duration), max_values['max_playlist_duration'])

    elif platform in ["Coursera", "Class Central"]:
        views_score = 0  # No views for courses
        likes_score = normalize(convert_to_number(likes), max_values['max_course_reviews'])
        duration_score = normalize(convert_duration_to_hours(duration), max_values['max_course_duration'])

    # Normalize published date
    date_score = calculate_date_score(published_on)

    # Calculate final score (40% likes/reviews, 30% views, 20% duration, 10% date)
    final_score = (likes_score * 0.4) + (views_score * 0.3) + (duration_score * 0.2) + (date_score * 0.1)
    
    return round(final_score, 2), views_score, likes_score, duration_score, date_score 

# Normalization helper
def normalize(value, max_value):
    try:
        return min((value / max_value) * 100, 100)
    except ZeroDivisionError:
        return 0



import sqlite3

def create_normalized_resources_db():
    conn = sqlite3.connect('normalized_skillnav.db')
    c = conn.cursor()

    # Create a new table to store the normalized data
    c.execute('''
        CREATE TABLE IF NOT EXISTS normalized_resources (
            id INTEGER PRIMARY KEY,
            category TEXT NOT NULL,
            title TEXT,
            creator TEXT,
            platform TEXT,
            type TEXT,
            duration TEXT,
            views TEXT,
            likes TEXT,
            published_on TEXT,
            description TEXT,
            score REAL,
            link TEXT ,
            thumbnail TEXT,
            difficulty TEXT,
            view_score INTEGER,
            like_score INTEGER,
            duration_score INTEGER,
            date_score INTEGER
        
        )
    ''')

    conn.commit()
    conn.close()

# Function to fetch, clean, normalize, and store data in the new database
def normalize_and_store_resources():
    conn = sqlite3.connect('skillnav.db')
    c = conn.cursor()

    # Fetch raw data from skillnav.db
    c.execute("SELECT id, category, title, creator, platform, type, duration, views, likes, published_on, description, link, thumbnail, difficulty FROM resources")
    resources = c.fetchall()

    # Get max values for normalization
    max_values = get_max_values(c)

    conn_normalized = sqlite3.connect('normalized_skillnav.db')
    c_normalized = conn_normalized.cursor()

    for resource in resources:
        score , vs , ls , ds , datsc = normalize_resource(resource, max_values)
        
        # Store the normalized resource in the new database
        c_normalized.execute('''
            INSERT OR REPLACE INTO normalized_resources 
            (id, category, title, creator, platform, type, duration, views, likes, published_on, description, score, link, thumbnail, difficulty, view_score, like_score, duration_score, date_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (resource[0], resource[1], resource[2], resource[3], resource[4], resource[5], resource[6],
              resource[7], resource[8], resource[9], resource[10], score, resource[11], resource[12], resource[13], vs, ls, ds, datsc))

    conn_normalized.commit()
    conn_normalized.close()
    conn.close()

# Run the functions
create_normalized_resources_db()
normalize_and_store_resources()


import sqlite3

def sort_and_update_ids():
    # Connect to the normalized_resources database
    conn = sqlite3.connect('normalized_skillnav.db')
    c = conn.cursor()

    # Step 1: Fetch all records, sorted by score in descending order
    c.execute("SELECT * FROM normalized_resources ORDER BY score DESC")
    resources = c.fetchall()

    # Step 2: Assign temporary IDs to avoid conflicts with the UNIQUE constraint
    temp_id = -1  # Start with a temporary negative ID
    temp_id_map = {}  # Dictionary to map original ID to temporary ID

    for resource in resources:
        resource_id = resource[0]  # Current ID of the resource
        # Assign a temporary negative ID and map it
        temp_id_map[resource_id] = temp_id
        c.execute("UPDATE normalized_resources SET id = ? WHERE id = ?", (temp_id, resource_id))
        temp_id -= 1
    
    # Step 3: Assign new IDs based on the sorted order
    new_id = 1
    for resource in resources:
        original_resource_id = resource[0]  # Original ID
        temp_resource_id = temp_id_map[original_resource_id]  # Get temporary ID from the map
        # Update the ID to match the new ranking order
        c.execute("UPDATE normalized_resources SET id = ? WHERE id = ?", (new_id, temp_resource_id))
        new_id += 1

    # Step 4: Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("IDs updated successfully based on the sorted scores!")

# Run the function
sort_and_update_ids()


