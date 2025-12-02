from flask import Flask, request, jsonify, render_template, send_from_directory, send_file
import folium
import sqlite3
import os

app = Flask(__name__)
db_file = "locations.db"
image_file = "intruder.jpg"

# Initialize Database
def init_db():
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    latitude REAL,
                    longitude REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

@app.route('/background.jpg')
def background():
    return send_from_directory('.', 'background.jpg')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/capture_location_image', methods=['POST'])
def capture_location_image():
    try:
        # Get location data
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        # Get Image
        if 'image' in request.files:
            image = request.files['image']
            image.save(image_file)

        # Save Location to Database
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute("INSERT INTO locations (latitude, longitude) VALUES (?, ?)", (latitude, longitude))
        conn.commit()
        conn.close()

        # Generate the Map
        map_ = folium.Map(location=[float(latitude), float(longitude)], zoom_start=15)
        folium.Marker([float(latitude), float(longitude)], popup='Intruder Location').add_to(map_)

        # Save the Map on Desktop
        desktop = os.path.join(os.path.expanduser("~"), 'Desktop')
        file_path = os.path.join(desktop, 'intruder_location.html')

        with open(file_path, 'w') as f:
            f.write('<!DOCTYPE html><html><head><title>Location</title></head><body>')
            f.write(map_._repr_html_())
            f.write('</body></html>')

        return jsonify({"status": "success", "message": "Location & image captured!"})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/intruder.jpg')
def get_image():
    if os.path.exists(image_file):
        return send_file(image_file, mimetype='image/jpeg')
    return jsonify({'status': 'error', 'message': 'No image found'})

if __name__ == '__main__':
    init_db()
    app.run(port=8000, debug=True)
