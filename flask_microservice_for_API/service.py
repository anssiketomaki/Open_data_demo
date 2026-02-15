from flask import Flask, request, jsonify
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import os
import requests

app = Flask(__name__)

# DATASETS
DATASETS = {
    "p": "https://data.fingrid.fi/api/datasets/74/data", # production
    "c": "https://data.fingrid.fi/api/datasets/124/data", # consumption
}
MAX_DAYS = 75
API_KEY = os.getenv("FINGRID_API_KEY")

def previous_full_quarter(dt=None):
    """
    Returns the datetime of the last full quarter of an hour
    
    :param dt: Datetime startingpoint
    """

    if dt is None:
        dt = datetime.now(timezone.utc)
    minute = (dt.minute // 15) * 15
    floored = dt.replace(minute=minute, second=0, microsecond=0)
    if floored == dt.replace(second=0, microsecond=0):
        floored -= timedelta(minutes=15)
    return floored

@app.route('/data', methods=['GET'])
def get_data():
    """
    Orchestrates data fetching process from the API
    """
    dataset_type = request.args.get("type")
    days_param = request.args.get("days", "0")
    
    try:
        days = int(days_param)
    except ValueError:
        return jsonify({"error": "Days must be an integer"}), 400

    if dataset_type not in DATASETS:
        return jsonify({"error": "Invalid dataset type. Use 'p' or 'c'."}), 400

    if days < 0 or days > MAX_DAYS:
        return jsonify({"error": f"Days out of range (0-{MAX_DAYS})"}), 400

    try:
        raw = fetch_raw_data(DATASETS[dataset_type], days)
        processed = aggregate(raw, days)
        return jsonify({"data": processed})
    
    except requests.exceptions.HTTPError as e:
        # Check if Fingrid rejected the key
        if e.response.status_code in [401, 403]:
            return jsonify({"error": "Fingrid API rejected the request. Is your API_KEY set correctly in the .env file?"}), 401
        return jsonify({"error": f"Fingrid API Error: {str(e)}"}), 502
    
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

def aggregate(data_points, days):
    """
    Aggregate/reduce data points to help visualizing the data 
    
    :param data_points: Fetched db datapoints
    :param days: Query parameter of period length
    """

    if not data_points:
        return []

    # Helper to parse time
    def parse_time(t_str):
        return datetime.fromisoformat(t_str.replace("Z", "+00:00"))

    grouped = defaultdict(list)
    
    # --- GROUPING STRATEGY ---
    if days == 0:
        # Strategy: "Today" -> Group by Hour
        # Format: HH:00
        for item in data_points:
            dt = parse_time(item["startTime"])
            key = dt.strftime("%H:00")
            grouped[key].append(item["value"])

    elif days <= 3:
        # Strategy: 1-3 Days -> Group by Hour (or 2-hour blocks if needed)
        # Format: Day HH:00
        for item in data_points:
            dt = parse_time(item["startTime"])
            key = dt.strftime("%d %H:00")
            grouped[key].append(item["value"])

    elif days <= 60:
        # Strategy: 4-60 Days -> Group by Day
        # Format: YYYY-MM-DD
        for item in data_points:
            dt = parse_time(item["startTime"])
            key = dt.strftime("%Y-%m-%d")
            grouped[key].append(item["value"])
            
    else:
        # Strategy: >60 Days -> Group by Week (ISO Week) to prevent 200 bars
        # Format: YYYY-Wxx
        for item in data_points:
            dt = parse_time(item["startTime"])
            # Format as "2024-W05"
            key = f"{dt.year}-W{dt.isocalendar()[1]:02d}"
            grouped[key].append(item["value"])

    # Calculate Averages
    result = []
    for key, values in grouped.items():
        avg = sum(values) / len(values)
        result.append({
            "label": key,
            "value": avg
        })
    
    # Sort alphabetically by label so the graph flows left-to-right correctly
    return sorted(result, key=lambda x: x['label'])

def fetch_raw_data(data_url, days):
    """
    Fetch the raw data from the set api
    
    :param data_url: dataset url to fetch data from
    :param days: amount of days for which to fetch data
    """
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
        "sortOrder": "desc",
        "pageSize": 20000,
    }
    
    response = requests.get(data_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    items = data.get("data", [])
    items.reverse()
    return items

if __name__ == "__main__":
    # Get port from args or env, default to 5001
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)