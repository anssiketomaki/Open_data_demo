# Open_data_demo
Python app that uses open data API to fetch data and present it for the user. Simple app.




This project was first just a microservice that was completed as a weekly coursework for University course. I made a container and CI/CD for it later.


# To run the application locally in Docker

0) Get your own API-key for the Fingrid API:
    - The database: https://data.fingrid.fi/
    - Instructions: https://data.fingrid.fi/instructions

1) Create a `.env` file in the `flask_microservice_for_api` folder and add your Fingrid API key:
    FINGRID_API_KEY="here_is_your_apikey_in_doublequotes"

2) Install Docker Desktop on your computer and make sure it is running.

3) Open a terminal (or Command Prompt) to the project root folder, where there is the compose.yml-file present

4) Build project in Docker using the following command (2 containers):
    docker compose up

5) Run the Docker container with the following command:
    docker run -p 5000:5000 flask-weather-service

6) The app should now be running inside the Docker container and accessible at port 5000 on your local machine. 
   You can use the microservice via browser or other tools (like `curl`) by accessing localhost at port 5000.
   For example:
       http://localhost:5000/weather?city=tampere


# The Databases used in the app
1) OpenWeatherMap Geocoding API
    - for fetching the latitude and longitude of the user-given cityname

2) OpenWeatherMap Current weather data API
    - for fetching the most recent measured weather data from the user determined location