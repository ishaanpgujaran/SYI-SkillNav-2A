from flask import Flask, render_template
import sqlite3

# Initialize the Flask app
app = Flask(__name__)

# Route for the Homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route for Web Development Page
#@app.route('/web-development')
#def webdev():
    return render_template('webdev.html')

@app.route('/web-devlopment')
def webdev():
    conn = sqlite3.connect('skillnav.db')
    c = conn.cursor()
    
    # Fetch the top 5 resources for "Top Resources"
    c.execute("""
        SELECT title, creator, description, platform, duration, views, likes, published_on, link, thumbnail, type, difficulty 
        FROM resources 
        WHERE category = 'Web Development' 
        ORDER BY views DESC LIMIT 5
    """)
    top_resources = c.fetchall()
    print("Top Resources:", top_resources)  # Debugging statement

    # Fetch all resources for "All Resources"
    c.execute("""
        SELECT title, creator, description, platform, duration, views, likes, published_on, link, thumbnail, type, difficulty 
        FROM resources 
        WHERE category = 'Web Development' 
        ORDER BY views DESC
    """)
    all_resources = c.fetchall()
    print("All Resources:", all_resources)  # Debugging statement

    conn.close()
    
    return render_template('webdev.html', top_resources=top_resources, all_resources=all_resources)

# Route for DSA Page
@app.route('/dsa')
def dsa():
    return render_template('dsa.html')

# Route for About Us Page
@app.route('/about')
def about():
    return render_template('about.html')

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
