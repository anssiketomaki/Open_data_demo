from flask import Flask, request, jsonify
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import os
import requests


app = Flask(__name__)

# URL's and key (set your 'API_KEY' into .env -file!)
DATASETS = {
    "p": "https://data.fingrid.fi/api/datasets/74/data", # production
    "c": "https://data.fingrid.fi/api/datasets/124/data", # consumption
}
API_KEY = os.getenv("FINGRID_API_KEY")


def previous_full_quarter(dt=None):
    """
    Returns the previous full quarter hour as a datetime object. If dt is None, uses the current time.
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    # Floor minute to previous quarter
    minute = (dt.minute // 15) * 15

    floored = dt.replace(minute=minute, second=0, microsecond=0)

    # If already exactly on quarter, go one quarter back
    if floored == dt.replace(second=0, microsecond=0):
        floored -= timedelta(minutes=15)

    return floored

@app.route('/data', methods=['GET'])
def get_data():
    dataset_type = request.args.get("type")
    days = int(request.args.get("days", 0))

    if dataset_type not in DATASETS:
        return jsonify({"error": "Invalid dataset type"}), 400

    if days < 0 or days > 364:
        return jsonify({"error": "Days out of range"}), 400

    raw = fetch_raw_data(DATASETS[dataset_type], days)
    processed = aggregate(raw, days)

    return jsonify(processed)

def aggregate(data_points, days):

    # ≤7 days → raw
    if days <= 7:
        return data_points

    grouped = defaultdict(list)

    for item in data_points:
        dt = datetime.fromisoformat(item["startTime"].replace("Z", "+00:00"))

        if days <= 31:
            key = dt.date()  # daily aggregation
        else:
            key = (dt.year, dt.month)  # monthly aggregation

        grouped[key].append(item["value"])

    result = []

    for key, values in grouped.items():
        avg = sum(values) / len(values)
        result.append({
            "period": str(key),
            "value": avg
        })

    return result

def fetch_raw_data(data_url, days):
    """
    Endpoint to fetch electricity production data for today.
    """
    end_time = previous_full_quarter()
    start_time = end_time - timedelta(days=days)

    headers = {
        "x-api-key": API_KEY,
        "Cache-Control": "no-cache",
    }
    
    params = {
        "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "format": "json",
        "locale": "en",
        "sortBy": "startTime",
        "sortOrder": "asc",
    }
    
    response = requests.get(
        data_url,
        headers=headers,
        params=params
    )

    data = response.json()

    if not data.get("data"):
        raise RuntimeError("No data returned")

    return data["data"]

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
