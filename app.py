from flask import Flask, render_template, request, jsonify
import sqlite3
import json

app = Flask(__name__)

# Function to get database connection
def get_db_connection():
    conn = sqlite3.connect('albums.db')
    conn.row_factory = sqlite3.Row  # Allows column access by name
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    title = data.get('title', '')
    artist = data.get('artist', '')
    genres = data.get('genre', [])
    styles = data.get('style', [])  # Get styles from the request
    years = data.get('year', [])

    conn = get_db_connection()
    cursor = conn.cursor()

    # Build the base SQL query
    query = "SELECT * FROM album WHERE 1=1"
    params = []

    # Add conditions based on search fields
    if title:
        query += " AND title LIKE ?"
        params.append(f'%{title}%')
    
    if artist:
        query += " AND artist LIKE ?"
        params.append(f'%{artist}%')
    
    if genres:
        genre_conditions = " OR ".join("genre LIKE ?" for _ in genres)
        query += f" AND ({genre_conditions})"
        params.extend([f'%{genre}%' for genre in genres])
    
    if styles:  # Check for styles
        style_conditions = " OR ".join("style LIKE ?" for _ in styles)
        query += f" AND ({style_conditions})"
        params.extend([f'%{style}%' for style in styles])
    
    if years:
        query += " AND year BETWEEN ? AND ?"
        params.extend(years)

    # Execute the query
    cursor.execute(query, params)
    
    results = cursor.fetchall()
    conn.close()

    # Convert results to a list of dictionaries for JSON response
    albums = []
    for row in results:
        tracklist = json.loads(row["tracklist"]) if row["tracklist"] else []
        albums.append({
            "id": row["id"],
            "title": row["title"],
            "artist": row["artist"],
            "tracklist": tracklist,
            "shelf_label": row["shelf_label"],
            "cover_image": row["cover_image"],
            "style": row["style"],
            "genre": row["genre"],
            "year": row["year"],
            "discogs_link": row["discogs_link"]  # Include the discogs_link in the response
        })

    return jsonify(albums)

if __name__ == '__main__':
    app.run(debug=True)
