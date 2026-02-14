import sys
import requests
import shutil

# This points to the service container name defined in compose.yml
SERVICE_URL = "http://service:5001/data"

def print_ascii_chart(data):
    """
    Plots a simple bar chart in the terminal.
    Expects data = [{'label': '10:00', 'value': 123.4}, ...]
    """
    if not data:
        print("No data to plot.")
        return

    # Dimensions
    terminal_width = shutil.get_terminal_size((80, 20)).columns
    max_label_len = max(len(d['label']) for d in data)
    chart_width = terminal_width - max_label_len - 5  # space for label + separator
    
    values = [d['value'] for d in data]
    min_val = 0 # Assume energy isn't negative usually, or min(values)
    max_val = max(values) if values else 1

    print(f"\n--- Data Visualization (Max: {max_val:.2f}) ---")
    
    for item in data:
        val = item['value']
        label = item['label']
        
        # Calculate bar length
        bar_len = int((val / max_val) * chart_width)
        bar = '█' * bar_len
        
        print(f"{label.ljust(max_label_len)} | {bar} {val:.0f}")
    print("\n")

def parse_input(user_input):
    user_input = user_input.strip().lower()
    if user_input == 'q':
        return 'q', 0
    
    if len(user_input) < 2:
        raise ValueError("Input too short (e.g., p0, c7)")
        
    dataset = user_input[0]
    days_str = user_input[1:]
    
    if dataset not in ('p', 'c'):
        raise ValueError("Start with 'p' (production) or 'c' (consumption)")
    
    if not days_str.isdigit():
        raise ValueError("Time must be a number")
        
    return dataset, int(days_str)

def ui():
    print("--- Fingrid Open Data CLI ---")
    print("Commands: [p/c][days] (e.g., 'p0' = production today, 'c7' = consumption week)")
    print("Type 'q' to quit.")

    while True:
        try:
            user_input = input("\nFetch > ")
            dataset, days = parse_input(user_input)
            
            if dataset == 'q':
                print("Bye!")
                break

            print(f"Fetching data for '{dataset}' over {days} days...")
            
            response = requests.get(
                SERVICE_URL, 
                params={"type": dataset, "days": days}
            )
            response.raise_for_status()
            
            json_resp = response.json()
            
            if "error" in json_resp:
                print(f"Server Error: {json_resp['error']}")
            else:
                print_ascii_chart(json_resp.get("data", []))

        except ValueError as e:
            print(f"Input Error: {e}")
        except requests.exceptions.ConnectionError:
            print(f"Network Error: Could not connect to {SERVICE_URL}. Is the service running?")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    ui()