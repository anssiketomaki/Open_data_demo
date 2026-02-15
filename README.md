# Open_data_demo
Full Python app that fetches and shows data for user in commandline. The app is used with simple commands. Data is from Fingrid open data API where two datasets are used: Finland's electricity consumption and production. The app is to be launched with Docker.

This app was made as a weekly task for a University course.

Project GitHub page: https://github.com/anssiketomaki/Open_data_demo

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


# Example run and output
```
~/github/Open_data_demo$ docker compose up -d

    (....container building phases.....)

~/github/Open_data_demo$ docker compose run --rm client

    (....container building phases.....)


--- Fingrid Open Data CLI ---
Commands: [p/c][days] (e.g., 'p0' = production today, 'c6' = consumption past week)
Database unit: MWh/h | Shown data = calculated averages from the 15min resolution in db.
App time = UTC+0
Type 'q' to quit.

Fetch > c30
Fetching data for 'c' over 31 days...

--- Data Results (Max: 14,451) ---
2026-01-16      | ██████████████████████████        12786
2026-01-17      | █████████████████████████         12090
2026-01-18      | ██████████████████████            10636
2026-01-19      | ███████████████████████           11107
2026-01-20      | ███████████████████████           11330
2026-01-21      | ████████████████████████          11843
2026-01-22      | █████████████████████████         12403
2026-01-23      | ██████████████████████████        12856
2026-01-24      | █████████████████████████         12513
2026-01-25      | █████████████████████████         12274
2026-01-26      | ██████████████████████████        12526
2026-01-27      | █████████████████████████         12471
2026-01-28      | ██████████████████████████        12973
2026-01-29      | ███████████████████████████       13346
2026-01-30      | ████████████████████████████      13792
2026-01-31      | █████████████████████████████     14240
2026-02-01      | ██████████████████████████████    14451
2026-02-02      | █████████████████████████████     14243
2026-02-03      | █████████████████████████████     13995
2026-02-04      | ████████████████████████████      13749
2026-02-05      | █████████████████████████████     14005
2026-02-06      | ████████████████████████████      13763
2026-02-07      | ███████████████████████████       13218
2026-02-08      | ███████████████████████████       13056
2026-02-09      | ██████████████████████████        12690
2026-02-10      | █████████████████████████         12455
2026-02-11      | ██████████████████████████        12538
2026-02-12      | ███████████████████████████       13018
2026-02-13      | ████████████████████████████      13749
2026-02-14      | ████████████████████████████      13738
2026-02-15      | ███████████████████████████       13008
----------------------------------------------------------

Fetch > p0
Fetching data for 'p' over 1 days...

--- Data Results (Max: 11,193) ---
00:00           | ██████████████████████████████    11193
01:00           | █████████████████████████████     10982
----------------------------------------------------------

Fetch > q
Bye!
```