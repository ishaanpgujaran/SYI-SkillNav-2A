from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sqlite3

def coursera_scraper():
    # Set up Selenium WebDriver
    driver_path = "./chromedriver"
    service = Service(driver_path)
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)  # Set up an explicit wait with a timeout of 10 seconds

    # Open Coursera search page for Web Development tutorials
    driver.get("https://www.coursera.org/search?query=data%20structure%20and%20algorithm")
    time.sleep(5)  # Wait for the page to fully load
    
    # Scroll to load more courses (we'll scroll 2 times to load more content)
    scroll_down(driver, scroll_pause_time=3, max_scrolls=1)
    
    # Find course elements
    courses = driver.find_elements(By.XPATH, '//li[@class="cds-9 css-0 cds-11 cds-grid-item cds-56 cds-64 cds-76 cds-90"]')

    # Limit to only the first 10 results
    courses = courses[:5]

    if courses:
        print(f"Found {len(courses)} courses on Coursera. Extracting data...")
        
        # Connect to the database
        conn = sqlite3.connect('skillnav.db')
        c = conn.cursor()
        
        for course in courses:
            try:
                # Extract Course Title
                try:
                    title_element = course.find_element(By.XPATH, './/h3[@class="cds-CommonCard-title css-6ecy9b"]')
                    title = title_element.text.strip() if title_element else "No title"
                except Exception as e:
                    print(f"Error extracting title: {e}")
                    continue
                
                # Extract Course URL
                try:
                    url_element = course.find_element(By.XPATH, './/a[@class="cds-119 cds-113 cds-115 cds-CommonCard-titleLink css-si869u cds-142"]')
                    course_url = url_element.get_attribute('href') if url_element else "No URL"
                except Exception as e:
                    print(f"Error extracting URL: {e}")
                    course_url = "No URL"
                
                # Extract Thumbnail URL
                thumbnail_url = "N/A"
                try:
                    # Attempt to find the img element within the first structure
                    thumbnail_element = course.find_element(By.XPATH, './/div[@class="cds-ProductCard-gridPreviewContainer"]//img')
                    if not thumbnail_element:
                        # Attempt to find the img element within the second structure
                        thumbnail_element = course.find_element(By.XPATH, './/div[@class="cds-CommonCard-previewImage"]//img')
                    
                    thumbnail_url = thumbnail_element.get_attribute('src') if thumbnail_element else "N/A"
                except Exception as e:
                    print(f"Error extracting thumbnail URL: {e}")
                    thumbnail_url = "N/A"

                
                
                # Extract Creator
                creator = "N/A"
                try:
                    creator_element = course.find_element(By.XPATH, './/div[@class="css-cxybwo cds-ProductCard-partners"]')
                    creator = creator_element.get_attribute('title').strip() if creator_element else "Unknown"
                except Exception as e:
                    print(f"Error extracting instructor name: {e}")
                    creator = "Unknown"

                # Extract Course Description
                description = "N/A"
                try:
                    description_element = course.find_element(By.XPATH, './/p[@class=" css-vac8rf"]')
                    description = description_element.text.strip() if description_element else "No description"
                except Exception as e:
                    print(f"Error extracting description: {e}")
                    description = "No description"
                
                #Extract Ratings & Reviews
                course_rating =  "N/A"
                course_review = "N/A"
                try:
                    c_rating_element = course.find_element(By.XPATH, './/p[@class="css-1whdyhf"]')
                    course_rating =  c_rating_element.text.strip() if c_rating_element else "N/A"

                    c_review_element = course.find_element(By.XPATH, './/div[@class="product-reviews css-pn23ng"]/p[@class=" css-vac8rf"]')
                    #c_review_t = c_review_element.text.strip()
                    course_review = c_review_element.text.strip('()') if c_review_element else "N/A"

                except Exception as e:
                    print(f"Error extracting ratings: {e}")
                    course_rating = "No Rating"
                    print(f"Error extracting reviews: {e}")
                    course_review = "No Reviews"
                
                # Extract Course Duration
                duration = "N/A"
                difficulty = "N/A"
                try:
                    d_element = course.find_element(By.XPATH, './/div[@class="cds-CommonCard-metadata"]/p[@class=" css-vac8rf"]')
                    d_text = d_element.text.strip() if d_element else "N/A"
                    
                    difficulty = d_text.split('·')[0].strip() if difficulty else "N/A"

                    duration = d_text.split('·')[2].strip() if difficulty else "N/A"
                except Exception as e:
                    print(f"Error extracting duration: {e}")
                    duration = "N/A"

                # Insert into the database
                c.execute('''
                    INSERT INTO resources (category, title, creator, description, platform, duration, views, likes, published_on, link, thumbnail, type, difficulty)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', ('DSA', title, creator, description, 'Coursera', duration, course_rating, course_review , 'Up to date', course_url, thumbnail_url, 'Course', difficulty))
                
                print(f"Added Coursera Course: {title}")

            except Exception as e:
                print(f"Error extracting data for a course: {e}")
        
        conn.commit()
        conn.close()
        print("Data successfully added to the database!")
    else:
        print("No courses found.")
    
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
coursera_scraper()
