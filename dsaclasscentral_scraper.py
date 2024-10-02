from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import sqlite3
import time


def class_central_scraper():
    # Set up Selenium WebDriver
    driver_path = "./chromedriver"  # Adjust path to where your chromedriver is located
    service = Service(driver_path)
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=service, options=options)
    
    # Open Class Central's web development search page with "free" filter
    class_central_url = "https://www.classcentral.com/search?q=data+structure+and+algorithm&free=true"
    driver.get(class_central_url)
    time.sleep(5)  # Allow time for the page to fully load

    # Scroll to load more ccourses (we'll scroll 2 times to load more content)
    scroll_down(driver, scroll_pause_time=3, max_scrolls=0)

    # Connect to the database
    conn = sqlite3.connect('skillnav.db')
    c = conn.cursor()
    
    # Find all course elements on the page
    ccourses = driver.find_elements(By.XPATH, '//li[@class="bg-white border-all border-gray-light padding-xsmall radius-small margin-bottom-small medium-up-padding-horz-large medium-up-padding-vert-medium course-list-course"]')

    # Limit to only the first 10 results
    ccourses = ccourses[:10]
    
    if ccourses:
        print(f"Found {len(ccourses)} ccourses. Extracting data...")

        for course in ccourses:
            try:
                # Extract the course title
                title_element = course.find_element(By.XPATH, './/h2[contains(@class, "text-1 weight-semi line-tight margin-bottom-xxsmall")]')
                title = title_element.text.strip() if title_element else "No Title"
                
                # Extract the creator/instructor
                try:
                    creator_element = course.find_element(By.XPATH, './/img[@class="block"]')
                    creator = creator_element.get_attribute('title') 
                except :
                    try:
                        # Locate the 'a' tag with the specified class within the span tag
                        creator_element = course.find_element(By.XPATH, './/span[@class="margin-right-xsmall"]/a')

                        # Extract the 'data-track-props' attribute
                        data_track_props = creator_element.get_attribute('data-track-props')

                        # Check if 'data-track-props' exists and parse it
                        if data_track_props:
                            # Parse the JSON-like string to extract 'catalog_title'
                            import json
                            data_props = json.loads(data_track_props.replace('&quot;', '"'))
                            creator = data_props.get('catalog_title', "Unknown Creator")
                    except:
                            creator = "Unknown Creator"
                
                
                # Extract the description (Short snippet/summary)
                try:
                    description_element = course.find_element(By.XPATH, './/a[@class="color-charcoal block hover-no-underline break-word"]')
                    description = description_element.text.strip()
                except:
                    description = "No description available"
                
                # Extract the platform (e.g., Coursera, edX, Udemy, etc.)
                platform_element = course.find_element(By.XPATH, './/a[@class="hover-underline color-charcoal text-3 margin-left-small line-tight"]')
                platform = platform_element.text.strip() if platform_element else "Unknown Platform"
                
                # Extract course duration
                try:
                    duration_element = course.find_element(By.XPATH, './/span[contains(@class, "text-3 margin-left-small line-tight")]')
                    duration = duration_element.text.strip()
                except:
                    duration = "Duration not specified"
                
                # Reviews will be treated as "likes" in our database
                try:
                    reviews_element = course.find_element(By.XPATH, './/span[@class="text-3 color-gray margin-left-xxsmall"]')
                    likes = reviews_element.text.strip()
                except:
                    likes = "No reviews"
                
                # As published date isn't available, we'll set it as "Up to date"
                published_on = "Up to date"

                # Extract course link
                link_element = course.find_element(By.XPATH, './/a[@class="medium-down-width-100 ratio ratio-9-16 hover-no-underline bg-gray-light radius-small shadow-light margin-bottom-xxsmall"]')
                link = link_element.get_attribute('href') if link_element else "No URL"
                
                # Extract the thumbnail URL
                try:
                    thumbnail_element = course.find_element(By.XPATH, './/img[@class="absolute top left width-100 height-100 cover block"]')
                    thumbnail = thumbnail_element.get_attribute('src')
                except:
                    thumbnail = "No Thumbnail"
                
                # Insert the data into the database
                c.execute('''
                    INSERT INTO resources (category, title, creator, description, platform, duration, views, likes, published_on, link, thumbnail, type, difficulty)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', ('DSA', title, creator, description, platform, duration, '', likes, published_on, link, thumbnail, 'Course', ''))
                
                print(f"Added Course: {title}")

            except Exception as e:
                print(f"Error extracting data for a course: {e}")
        
        conn.commit()
        conn.close()
        print("Data successfully added to the database!")
    else:
        print("No ccourses found.")
    
    # Close the WebDriver
    driver.quit()


def scroll_down(driver, scroll_pause_time=2, max_scrolls=1):
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
class_central_scraper()
