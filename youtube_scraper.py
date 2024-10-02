from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sqlite3
from youtube_api import (
    get_video_details,  get_playlist_details, 
    extract_video_id, extract_playlist_id, format_number, convert_published_date
)

#Using Selenium Extract Details of Web Development YouTube Resources

def youtube_scraper():
    # Set up Selenium WebDriver
    driver_path = "./chromedriver"
    service = Service(driver_path)
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)  # Set up an explicit wait with a timeout of 10 seconds
    
    # Open YouTube search page
    driver.get("https://www.youtube.com/results?search_query=web+development+tutorial")
    time.sleep(5)  # Wait for the page to fully load

    # Scroll to load more videos (only once as requested)
    scroll_down(driver, scroll_pause_time=3, max_scrolls=0)
    
    # Find video and playlist elements
    resources = driver.find_elements(By.XPATH, '//ytd-video-renderer | //ytd-playlist-renderer')

    # Limit to only the first 10 results
    resources = resources[:10]

    if resources:
        print(f"Found {len(resources)} resources. Extracting data...")
        
        # Connect to the database
        conn = sqlite3.connect('skillnav.db')
        c = conn.cursor()
        


        for resource in resources:
            try:
                #Identify Video or Playlist
                tagname = resource.tag_name

                #Extract Title & URL for Video
                if tagname == 'ytd-video-renderer':
                    title_element = resource.find_element(By.XPATH, './/*[@id="video-title"]')
                    title = title_element.get_attribute('title').strip()
                    
                    video_id = extract_video_id(title_element.get_attribute('href'))

                    url = title_element.get_attribute('href')
                    
                    resource_type = "Video"

                    creator_element = resource.find_element(By.XPATH, './/yt-formatted-string[@class="style-scope ytd-channel-name"]/a')
                    creator_name = creator_element.text.strip() if creator_element else "Unknown"


                    duration_element = resource.find_element(By.XPATH, './/span[@id="text" and @class="style-scope ytd-thumbnail-overlay-time-status-renderer"]')
                    duration = duration_element.get_attribute('aria-label') if duration_element else "N/A"

                    num_element = resource.find_element(By.XPATH, './/span[contains(text(), "views") and @class="inline-metadata-item style-scope ytd-video-meta-block"]')
                    num_views = num_element.text.strip() if num_element else "Unknown"

                    # Fetch additional details using YouTube Data API
                    description, thumbnail, likes, published_on = get_video_details(video_id)

                    # Insert into the database
                    c.execute('''
                        INSERT INTO resources (category, title, creator, description, platform, duration, views, likes, published_on, link, thumbnail, type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', ('Web Development', title, creator_name, description, 'YouTube', duration, num_views, likes, published_on, url, thumbnail, resource_type))
                    print(f"Added Video: {title}")



                #Extract Title & URL for Playlist
                elif tagname == 'ytd-playlist-renderer':
                    title_element = resource.find_element(By.XPATH, './/*[@id="video-title"]')
                    title = title_element.get_attribute('title').strip()
                    

                    urlelement =  resource.find_element(By.XPATH, './/yt-formatted-string[@id="view-more"]/a')
                    url = urlelement.get_attribute('href')


                    playlist_id = extract_playlist_id(url)
                    
                    resource_type = "Playlist"
                    
                    creator_element = resource.find_element(By.XPATH, './/yt-formatted-string[@id="text"]')
                    creator_fullname = creator_element.text.strip() if creator_element else "Unknown"
                    creator_name = creator_fullname.split('·')[0].strip()


                    playduration_element = resource.find_element(By.XPATH, './/yt-formatted-string[@class="style-scope ytd-thumbnail-overlay-bottom-panel-renderer"]')
                    duration_text = playduration_element.text.strip() if playduration_element else "N/A"
                    if 'lessons' in duration_text:
                        # Extract the number from the text
                        duration = duration_text.split('·')[1].strip() if duration_text != "N/A" else "N/A"
                    else:
                        duration = duration_text.strip() if duration_text != "N/A" else "N/A"
                        
                    
                    # Fetch additional details using YouTube Data API
                    description, thumbnail, num_views, likes, published_on = get_playlist_details(playlist_id)

                    """
                    num_videos = duration.split()[0].strip()
                    numv = int(num_videos)
                    num_views = format_number(avg_views * numv)
                    likes = format_number(avglikes * numv)
                    """


                    # Insert into the database
                    c.execute('''
                        INSERT INTO resources (category, title, creator, description, platform, duration, views, likes, published_on, link, thumbnail, type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', ('Web Development', title, creator_name, description, 'YouTube', duration, num_views, likes, published_on, url, thumbnail, "Playlist"))
                    print(f"Added Playlist: {title}")
                
                
                
        
                

                """ 
                #Extract Thumbnail URL
                thumbnail_url = "N/A"
                try:
                    #Thumbnail Try 1
                    #thumbnail_element = resource.find_element(By.XPATH, './/yt-image[@class="style-scope ytd-thumbnail"]/img')
                    
                    Thumbnail Try 2 
                    thumbnail_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, './/img[contains(@class, "yt-core-image yt-core-image--fill-parent-height yt-core-image--fill-parent-width yt-core-image--content-mode-scale-aspect-fill yt-core-image--loaded")]'))
                    )
                    

                    #Thumbnail Try 3
                    thumbnail_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, './/yt-image[@class="style-scope ytd-thumbnail"]/img'))
                    )
                    
                    thumbnail_url = thumbnail_element.get_attribute('src') if thumbnail_element else "N/A"

                except Exception as e:
                    print(f"Error extracting thumbnail URL: {e}")
                    thumbnail_url = "N/A"
                """
                
                


                """
                #Using the Above Created Functions
                if "watch?v=" in url:
                    video_id = extract_video_id(url)
                    #title, creator_name, description, thumbnail, views, likes, duration, published_on = get_video_details(video_id)
                    description, thumbnail, likes, published_on = get_video_details(video_id)


                elif "list=" in url:
                    playlist_id = extract_playlist_id(url)
                    #title, creator_name, description, thumbnail, views, duration, published_on = get_playlist_details(playlist_id)
                    description, thumbnail, published_on = get_playlist_details(playlist_id)
                    likes = "N/A"  # Playlists don’t have likes
                """


                """
                # Insert into the database
                c.execute('''
                    INSERT INTO resources (category, title, creator, description, platform, duration, views, likes, published_on, link, thumbnail, type, difficulty)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', ('Web Development', title, creator_name, description, 'YouTube', duration, num_views, likes , published_on, url, thumbnail, resource_type, ''))
                
                print(f"Added {resource_type}: {title}")
                """

            except Exception as e:
                print(f"Error extracting data for a resource: {e}")
        


        conn.commit()
        conn.close()
        print("Data successfully added to the database!")
    else:
        print("No resources found.")
    
    # Close the WebDriver
    driver.quit()






def scroll_down(driver, scroll_pause_time=2, max_scrolls=0):
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    
    for _ in range(max_scrolls):
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(scroll_pause_time)
        
        # Calculate new scroll height
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Call the function to scrape data
youtube_scraper()