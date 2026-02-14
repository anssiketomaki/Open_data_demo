
import os
import requests
from flask import Flask, jsonify
import matplotlib.pyplot as plt

from service import get_production_today

# times, values = extract_lists(data)

# plt.plot(times, values)
# plt.xticks(rotation=45)
# plt.show()

SERVICE_URL = "http://service:5000/data"
MAX_DAYS = 365

def extract_values(raw_json):
    data_points = raw_json.get("data", [])

    return [
        {
            "start": item["startTime"],
            "end": item["endTime"],
            "value": item["value"]
        }
        for item in data_points
    ]

def extract_lists(raw_json):
    data_points = raw_json.get("data", [])

    times = [item["startTime"] for item in data_points]
    values = [item["value"] for item in data_points]

    return times, values

def parse_input(user_input: str):
    """
    Validate and sanitize parse_input
    
    :param user_input: user input for data fetch
    :type user_input: str
    """

    user_input = user_input.strip().lower()

    if len(user_input)<2:
            raise ValueError("Input too short!")
        
    dataset = user_input[0]
    if dataset not in ("p", "c"):
        raise ValueError("Dataset must be 'p' or 'c'!")

    days_raw = user_input[1:]
    if not days.isdigit():
        raise ValueError("Days must be a non-negative integer number!")
    
    days = int(days_raw)

    if days < 0 or days > MAX_DAYS:
        raise ValueError(f"Days must be between 0 and {MAX_DAYS}")
    return dataset, days

def fetch_data(dataset, days):
    response = requests.get(SERVICE_URL, dataset, days)
    response.raise_for_status()

    data = response.json()

    if not data.get("data"):
        raise RuntimeError("No data returned from Fingrid API.")

    return data


def ui():
    app = Flask(__name__)
    print("Hello and welcome to the open data demo UI!")
    print("This UI works by inputting a simple code for the wanted data\n")
    print("1) use letter 'p' to get electricity production data or letter 'c' for consumption data\n" \
    "2) add timescale with an integer number - 0 for today, 1 for from yesterday to today, 6 for past week,..:\n")
    print("Examples:" \
    "production data of today: p0\n" \
    "consumption data of today: c0\n" \
    "production data of last week: p6\n")
    print("You can find the results of data fetches from the 'Output'-folder in project root!")

    while True:
        print("fetch data by giving code. 'q' for quit:")
        user_input = input("Enter code for data fetch: ")
        if user_input == "q":
            print("See ya!")
            break
        try:
            dataset, days = parse_input(user_input)
            data = fetch_data(dataset, days)
        except ValueError as e:
            print(f"Invalid input: {e}")
            continue
        except requests.RequestException as e:
            print("Network/API error:", e)
            continue
        except RuntimeError as e:
            print("Data error:", e)
            continue

        response = requests.get(
            SERVICE_URL,
            params={
                "type": "production",
                "days": 7
            }
        )

        data = response.json()



        plt.plot(times, values)
        plt.show()
        #app.add_url_rule('/prodtoday', 'get_production_today', get_production_today)


if __name__ == "__main__":
    ui()
