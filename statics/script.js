// Backend API URL
const BASE_URL = 'http://localhost:5000';

// Function to show home screen after login
function showHomeScreen(username) {
    document.getElementById('welcome-username').innerText = username;
    document.getElementById('login-container').style.display = 'none';
    document.getElementById('home-container').style.display = 'block';
    fetchCities();
}

// Function to fetch tracked cities from backend
function fetchCities() {
    axios.get(`${BASE_URL}/cities`)
        .then(response => {
            const cities = response.data;
            const cityList = document.getElementById('city-list');
            cityList.innerHTML = '';
            cities.forEach(city => {
                const li = document.createElement('li');
                li.innerText = `${city.city} - Temperature: ${city.temperature}°C, Humidity: ${city.humidity}%`;
                li.onclick = function() {
                    showCityDetails(city.city);
                };
                cityList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error fetching cities:', error);
        });
}

// Function to show city details popup
function showCityDetails(city) {
    axios.get(`${BASE_URL}/city/${city}`)
        .then(response => {
            const cityDetails = response.data;
            document.getElementById('city-name').innerText = cityDetails.city;
            document.getElementById('weather-info').innerText = `Temperature: ${cityDetails.temperature}°C, Humidity: ${cityDetails.humidity}%`;
            document.getElementById('city-details-container').style.display = 'block';
            // Here you can add logic to display trend graphs for temperature and humidity
        })
        .catch(error => {
            console.error('Error fetching city details:', error);
        });
}

// Function to add a new city
function addCity() {
    const newCity = document.getElementById('new-city').value;
    axios.post(`${BASE_URL}/cities`, { city: newCity })
        .then(response => {
            alert(response.data.message);
            fetchCities();
            closeAddCityPopup();
        })
        .catch(error => {
            console.error('Error adding city:', error);
        });
}

// Function to delete a city
function deleteCity() {
    const cityName = document.getElementById('city-name').innerText;
    axios.delete(`${BASE_URL}/cities?city=${cityName}`)
        .then(response => {
            alert(response.data.message);
            document.getElementById('city-details-container').style.display = 'none';
            fetchCities();
        })
        .catch(error => {
            console.error('Error deleting city:', error);
        });
}

// Function to show add city popup
function showAddCityPopup() {
    document.getElementById('add-city-popup').style.display = 'block';
}

// Function to close add city popup
function closeAddCityPopup() {
    document.getElementById('add-city-popup').style.display = 'none';
}

// Function to handle login
function login() {
    const username = document.getElementById('username').value;
    // Perform authentication (backend logic)
    // Assuming authentication is successful, show home screen
    showHomeScreen(username);
}

// Function to handle logout
function logout() {
    // Clear any user data or tokens stored in local storage
    document.getElementById('home-container').style.display = 'none';
    document.getElementById('login-container').style.display = 'block';
}
