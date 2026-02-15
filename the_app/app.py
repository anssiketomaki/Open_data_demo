import requests
import shutil

SERVICE_URL = "http://service:5001/data"
MAX_DAYS = 100

def print_ascii_chart(data):
    """
    Creates an ascii_chart from fetched data
    
    :param data: Fetched data from the Fingrid API
    """
    if not data:
        print("No data to plot.")
        return

    terminal_width = shutil.get_terminal_size((80, 20)).columns
    
    # Capping the bar width to 1/3 of the screen or 30 chars
    label_width = 15 
    value_width = 10
    max_bar_width = min(30, int(terminal_width * 0.4)) 

    values = [d['value'] for d in data]
    max_val = max(values) if values else 1

    print(f"\n--- Data Results (Max: {max_val:,.0f}) ---")
    
    for item in data:
        val = item['value']
        label = item['label']
        
        # Scale the bar
        fraction = val / max_val if max_val > 0 else 0
        bar_len = int(fraction * max_bar_width)
        
        bar = '█' * bar_len
            
        print(f"{label:<{label_width}} | {bar:<{max_bar_width}} {val:>8.0f}")
    print("-" * (label_width + max_bar_width + value_width + 3))

def parse_input(user_input: str):
    """
    Checks and validates the user input commands
    
    :param user_input: user input commad
    """
    user_input = user_input.strip().lower()
    if user_input == 'q':
        return 'q', 0
    
    if len(user_input) < 2:
        raise ValueError("Input too short (e.g., p0, c6)")
        
    dataset = user_input[0]
    days_str = user_input[1:]
    
    if dataset not in ('p', 'c'):
        raise ValueError("Start with 'p' (production) or 'c' (consumption)")
    
    if not days_str.isdigit():
        raise ValueError("Time must be a number")
    
    days = int(days_str)
    if days < 0 or days > MAX_DAYS:
        raise ValueError(f"Days must be between 0 and {MAX_DAYS} (API limit)")
        
    return dataset, days

def ui():
    """
    CMD ui
    """
    print("\n\n")
    print("--- Fingrid Open Data CLI ---")
    print("Commands: [p/c][days] (e.g., 'p0' = production today, 'c6' = consumption past week)")
    print("Database unit: MWh/h | Shown data = calculated averages from the 15min resolution in db.")
    print("App time = UTC+0")
    print("Type 'q' to quit.")

    while True:
        try:
            user_input = input("\nFetch > ")
            dataset, days = parse_input(user_input)
            
            if dataset == 'q':
                print("Bye!")
                break

            print(f"Fetching data for '{dataset}' over {days+1} days...")
            
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