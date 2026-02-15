# Open_data_demo
Full Python app that fetches and shows data for user. Used on commanline. Uses Fingrid open data API to fetch data. Made as a weekly task for University course.

# App structure
```
Open_data_demo/
├── compose.yml   # Multi-container build structure
├── .gitignore    # (Optional) To hide .env and __pycache__
│
├── flask_microservice_for_API/ # SERVICE CONTAINER
│   ├── service.py          # Flask API logic & Fingrid fetching
│   ├── Dockerfile.flask    
│   ├── requirements.txt
│   └── .env                # FINGRID_API_KEY="your_key"
│
└── the_app/                # CLIENT CONTAINER
    ├── app.py              # Interactive CLI & ASCII Plotter
    ├── Dockerfile.app      
    └── requirements.txt
```

# Prerequisites

1) Have Docker and Docker Compose installed. Or on windows have docker desktop installed and launched.

2) .env file in ./flask_microservice_for_API/ containing
```
    FINGRID_API_KEY="your_key_in_quotes"
```

Where to get API-key for the Fingrid API:

    - The database: https://data.fingrid.fi/
    - Instructions: https://data.fingrid.fi/instructions

# Run the application locally in Docker

1) Open a terminal (or Command Prompt) to the project root folder, where there is the compose.yml-file present

2) Build and start the data-fetching service in the background with
```
    docker compose up -d
```

3) Run the UI in the command line with:
```
    docker compose run --rm client
```

4) Fetch and view data: Supported range is today (0) plus max 75 days (= 76 days) to ensure the smooth operation of the app.
- Choose either c (consumption) or p (production)
- Choose how far back you would like to see:
    - 0 = last day
    - Additional numbers add days before today -> e.g. 6 = past week
- Combine the parameters to a command e.g. p0, c75,..

## Teardown
You can stop running containers from cmd at project root with
```
    docker compose down
```


# The Datasets used in the app
1) FINGRID Open Data: Electricity consumption in Finland
    - https://data.fingrid.fi/en/datasets/124

2) FINGRID Open Data: Electricity production in Finland
    - https://data.fingrid.fi/en/datasets/74
