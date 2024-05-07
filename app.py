import matplotlib
matplotlib.use('Agg') 

from flask import Flask, jsonify, request, render_template
import requests
import sqlite3
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import base64
import folium
from io import BytesIO
from flask import redirect, url_for, session
app = Flask(__name__)



# Create SQLite database
conn = sqlite3.connect('weather_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS cities
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)''')
c.execute('''CREATE TABLE IF NOT EXISTS weather_data
            (city_id INTEGER, temperature REAL, humidity REAL, timestamp DATETIME,
            FOREIGN KEY(city_id) REFERENCES cities(id))''')
conn.commit()
conn.close()

# Function to fetch weather data from external API
# Function to fetch weather data from external API
def fetch_weather_data(city):
    api_key = "d184b37c8a4aa14c023139d5c14c03d1"  # Replace with your API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if 'main' in data:
        # Convert temperature from Kelvin to Celsius and round to one digit after the decimal
        temperature_celsius = round(data['main']['temp'] - 273.15, 1)
        data['main']['temp'] = temperature_celsius
    
    return data

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Example: Validate credentials (Replace with your logic)
        if email == 'user@example.com' and password == 'password':
            # Set session variable to indicate user is logged in
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid email or password')
    else:
        return render_template('login.html')
# Function to save weather data to SQLite database
def save_weather_data(city_id, temperature, humidity):
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO weather_data VALUES (?, ?, ?, ?)", (city_id, temperature, humidity, timestamp))
    conn.commit()
    conn.close()

# Function to fetch trend data from SQLite database
def fetch_trend_data(city_id):
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    c.execute("SELECT temperature, humidity, timestamp FROM weather_data WHERE city_id=?", (city_id,))
    data = c.fetchall()
    conn.close()
    return data

# Modify your home route to provide JSON data when requested via AJAX
# Backend (Flask Application)
@app.route('/', methods=['GET'])
def home():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        conn = sqlite3.connect('weather_data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM cities")
        cities = c.fetchall()
        city_weather_data = []
        for city in cities:
            city_id, city_name = city
            weather_data = fetch_weather_data(city_name)
            if 'main' in weather_data:
                temperature = weather_data['main']['temp']
                humidity = weather_data['main']['humidity']
                weather_condition = get_weather_condition(temperature)
                city_weather_data.append({"city_id": city_id, "city_name": city_name, "temperature": temperature, "humidity": humidity, "weather_condition": weather_condition})
        conn.close()
        return jsonify({"city_weather_data": city_weather_data})
    else:
        return render_template('index.html')



def get_weather_condition(temperature):
    if temperature > 40:
        return "hot"
    elif temperature > 28:
        return "normal"
    else:
        return "pleasant"

@app.route('/add_city', methods=['POST'])
def add_city():
    city = request.form['city']
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO cities (name) VALUES (?)", (city,))
        conn.commit()
        message = "City added successfully."
    except sqlite3.IntegrityError:
        message = "City already exists."
    conn.close()
    return jsonify({"message": message})
@app.route('/delete_city/<int:city_id>', methods=['DELETE'])
def delete_city(city_id):
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM cities WHERE id=?", (city_id,))
    c.execute("DELETE FROM weather_data WHERE city_id=?", (city_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "City deleted successfully."})


@app.route('/weather', methods=['GET'])
def get_weather():
    city_id = request.args.get('city_id')
    city_name = request.args.get('city_name')
    weather_data = fetch_weather_data(city_name)
    temperature = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    save_weather_data(city_id, temperature, humidity)
    return jsonify(weather_data)

@app.route('/trend', methods=['GET'])
def get_trend():
    city_id = request.args.get('city_id')
    trend_data = fetch_trend_data(city_id)
    return jsonify(trend_data)

@app.route('/temperature_trend', methods=['GET'])
def temperature_trend():
    cities_data = fetch_all_cities_data()
    for city_data in cities_data:
        city_id = city_data['city_id']
        trend_data = fetch_trend_data(city_id)
        if trend_data:
            timestamps = [data[2] for data in trend_data]
            temperatures = [data[0] for data in trend_data]
            plt.plot(timestamps, temperatures, label=city_data['city_name'])
    
    plt.xlabel('Timestamp')
    plt.ylabel('Temperature (°C)')
    plt.title('Temperature Trend')
    plt.legend()
    
    # Save plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Encode plot to base64 string
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()  # Close the plot to release memory
    
    return jsonify({"temperature_trend": plot_data})

@app.route('/humidity_trend', methods=['GET'])
def humidity_trend():
    cities_data = fetch_all_cities_data()
    for city_data in cities_data:
        city_id = city_data['city_id']
        trend_data = fetch_trend_data(city_id)
        if trend_data:
            timestamps = [data[2] for data in trend_data]
            humidities = [data[1] for data in trend_data]
            plt.plot(timestamps, humidities, label=city_data['city_name'])
    
    plt.xlabel('Timestamp')
    plt.ylabel('Humidity (%)')
    plt.title('Humidity Trend')
    plt.legend()
    
    # Save plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Encode plot to base64 string
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()  # Close the plot to release memory
    
    return jsonify({"humidity_trend": plot_data})

def fetch_all_cities_data():
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM cities")
    cities_data = [{"city_id": city[0], "city_name": city[1]} for city in c.fetchall()]
    conn.close()
    return cities_data
   
@app.route('/trends', methods=['GET'])
def view_trends():
    return render_template('trends.html')
# Update Flask route to provide city data
@app.route('/map')
def weather_map():
    # Initialize map centered at a location
    weather_map = folium.Map(location=[0, 0], zoom_start=2)

    # Fetch cities data
    cities_data = fetch_all_cities_data()

    # Iterate over cities data and add markers to the map
    for city_data in cities_data:
        city_name = city_data['city_name']
        weather_data = fetch_weather_data(city_name)
        latitude = weather_data['coord']['lat']
        longitude = weather_data['coord']['lon']
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']

        # Create a marker with weather details in popup
        popup_text = f"City: {city_name}<br>Temperature: {temperature}°C<br>Humidity: {humidity}%"
        marker = folium.Marker(location=[latitude, longitude], popup=popup_text)
        marker.add_to(weather_map)

    # Save the map to an HTML file
    map_path = 'templates/weather_map.html'
    weather_map.save(map_path)

    return render_template('map.html', map_path=map_path)

if __name__ == '__main__':
    app.run(debug=True)
