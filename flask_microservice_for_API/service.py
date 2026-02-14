from flask import Flask, request, jsonify
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import os
import requests
import sys

app = Flask(__name__)

# DATASETS
DATASETS = {
    "p": "https://data.fingrid.fi/api/datasets/74/data", # production
    "c": "https://data.fingrid.fi/api/datasets/124/data", # consumption
}
API_KEY = os.getenv("FINGRID_API_KEY")

def previous_full_quarter(dt=None):
    if dt is None:
        dt = datetime.now(timezone.utc)
    minute = (dt.minute // 15) * 15
    floored = dt.replace(minute=minute, second=0, microsecond=0)
    if floored == dt.replace(second=0, microsecond=0):
        floored -= timedelta(minutes=15)
    return floored

@app.route('/data', methods=['GET'])
def get_data():
    dataset_type = request.args.get("type")
    days_param = request.args.get("days", "0")
    
    try:
        days = int(days_param)
    except ValueError:
        return jsonify({"error": "Days must be an integer"}), 400

    if dataset_type not in DATASETS:
        return jsonify({"error": "Invalid dataset type. Use 'p' or 'c'."}), 400

    if days < 0 or days > 364:
        return jsonify({"error": "Days out of range (0-364)"}), 400

    try:
        raw = fetch_raw_data(DATASETS[dataset_type], days)
        processed = aggregate(raw, days)
        return jsonify({"data": processed})
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

def aggregate(data_points, days):
    # Strategy: Always return a list of {label, value}
    # If viewing 1 day: Aggregate by Hour
    # If viewing > 1 day: Aggregate by Day
    
    grouped = defaultdict(list)
    
    for item in data_points:
        dt = datetime.fromisoformat(item["startTime"].replace("Z", "+00:00"))
        
        if days <= 1:
            # Group by Hour:HH
            key = dt.strftime("%H:00")
        else:
            # Group by Date: YYYY-MM-DD
            key = dt.strftime("%Y-%m-%d")

        grouped[key].append(item["value"])

    result = []
    for key, values in grouped.items():
        avg = sum(values) / len(values)
        result.append({
            "label": key,
            "value": avg
        })
    
    # Sort by label to ensure time continuity in plot
    return sorted(result, key=lambda x: x['label'])

def fetch_raw_data(data_url, days):
    end_time = previous_full_quarter()
    start_time = end_time - timedelta(days=days)

    if days == 0:
        # If today, start from midnight
        start_time = end_time.replace(hour=0, minute=0, second=0)

    headers = {"x-api-key": API_KEY}
    params = {
        "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "format": "json",
        "locale": "en",
        "sortBy": "startTime",
        "sortOrder": "asc",
    }
    
    response = requests.get(data_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("data", [])

if __name__ == "__main__":
    # Get port from args or env, default to 5001
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)