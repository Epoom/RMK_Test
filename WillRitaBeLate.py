import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import requests
import io


# === CONSTANTS & CONFIGURATION ===

# Define the coordinates for the Zoo and Toompea bus stops
ZOO_STOP_COORDS = (59.42621, 24.65889)
TOOMPEA_STOP_COORDS = (59.4368347, 24.7332953)

# Tallinn live transport data URL
LIVE_BUS_URL = "https://transport.tallinn.ee/gps.txt"


# === TIME CONVERSION ===

def time_to_seconds(t_str):
    """Convert a time string 'HH:MM' to seconds since midnight."""
    hour, minute = map(int, t_str.strip().split(":"))
    return hour * 3600 + minute * 60

def seconds_to_time(sec):
    """Convert seconds since midnight to HH:MM format."""
    hour = int(sec // 3600)
    minute = int((sec % 3600) // 60)
    return f"{hour:02d}:{minute:02d}"


# === FETCH LIVE DATA ===

def fetch_live_bus_data():
    
    """Fetch real-time bus positions from Tallinn transport feed with proper headers."""
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
	
    response = requests.get(LIVE_BUS_URL, headers=headers)
    
    if response.status_code == 200:
        return response.text  # Returns raw CSV-like text
    else:
        print(f"Error fetching real-time bus data. Status code: {response.status_code}")
        return None
    

def load_real_time_bus_data():
    """Fetch, process, and filter real-time bus data for Bus 8."""
    raw_data = fetch_live_bus_data()
    if raw_data is None:
        return None

    # Convert raw text into Pandas DataFrame
    df = pd.read_csv(io.StringIO(raw_data), header=None)

    # Define dataset column names based on known format
    df.columns = ["transport_type", "line_number", "longitude", "latitude",
                  "empty_field", "speed", "heading", "vehicle_type",
                  "vehicle_number", "location"]

    # Convert `line_number` column to integer for proper filtering
    df["line_number"] = pd.to_numeric(df["line_number"], errors="coerce")

    # Filter for Bus 8
    bus_8_df = df[df["line_number"] == 8]

    return bus_8_df if not bus_8_df.empty else None


# === IDENTIFY CLOSEST BUS ===

def get_next_bus_real_time(t_arrival_stop):
    """Fetch live bus data and determine the closest arriving bus at Zoo."""
    bus_df = load_real_time_bus_data()

    if bus_df is None or bus_df.empty:
        print("No live bus data available! Rita will definitely be late.")
        return None, float("inf")

    closest_bus = None
    shortest_distance = float("inf")

    for _, bus in bus_df.iterrows():
        bus_coords = (bus["latitude"] / 1e6, bus["longitude"] / 1e6)  # Convert to degrees
        distance_to_zoo = geodesic(bus_coords, ZOO_STOP_COORDS).km  # Distance in km

        if distance_to_zoo < shortest_distance:  # Find the closest bus
            closest_bus = bus
            shortest_distance = distance_to_zoo

    if closest_bus is None or closest_bus.empty:
        print("No Bus 8 found near Zoo!")
        return None, float("inf")

    # Estimate arrival time
    if closest_bus["speed"] > 0:  # Ensure speed is valid
        arrival_minutes = shortest_distance / (closest_bus["speed"] / 40)  # km per minute
        arrival_time_sec = t_arrival_stop + (arrival_minutes * 40)

        return closest_bus, arrival_time_sec - t_arrival_stop  # Return bus and wait time

    return closest_bus, float("inf")


# === SIMULATING RITA'S COMMUTE ===

# Define constants
MEETING_TIME = time_to_seconds("09:05")
HOME_TO_BUS_STOP = 300  # 300 seconds = 5 minutes
BUS_STOP_TO_MEETING = 240  # 240 seconds = 4 minutes

# Simulate Rita leaving home at different times
departure_times = np.arange(time_to_seconds("07:30"), time_to_seconds("09:05"), 60)  # Every minute
results = []

for dep_time in departure_times:
    arrival_at_bus_stop = dep_time + HOME_TO_BUS_STOP
    bus, wait_time = get_next_bus_real_time(arrival_at_bus_stop)

    if bus is not None and not bus.empty:
        arrival_at_meeting = arrival_at_bus_stop + wait_time + BUS_STOP_TO_MEETING
        late = arrival_at_meeting > MEETING_TIME
    else:
        late = True  # No available bus means Rita is late

    results.append({"DepartureTime": seconds_to_time(dep_time), "Late": late})


# === CONFIGURE AND SAVE RESULTS ===

# Convert results into a DataFrame for analysis
results_df = pd.DataFrame(results)
# Modify the results format
results_df["Late"] = results_df["Late"].map({True: "Late", False: "Not Late"})

# Print updated results
results_df.to_csv("rita_lateness_results.csv", index=False)
print("Results successfully saved to 'rita_lateness_results.csv'")


# === GENERATE PROBABILITY GRAPH ===

# Convert "Late" column to numeric values for plotting
results_df["LateNumeric"] = results_df["Late"].map({"Late": 1, "Not Late": 0})

# Create the figure
plt.figure(figsize=(10, 5))

# Plot the smooth probability curve
plt.plot(results_df["DepartureTime"], results_df["LateNumeric"].rolling(5).mean(), linestyle='-', color='red', label="Probability Curve")

# Format x-axis labels to show only every 5 minutes
tick_positions = results_df.iloc[::5]["DepartureTime"]  # Show every 5th entry
plt.xticks(tick_positions, rotation=45)

# Formatting the graph
plt.xlabel("Departure Time")
plt.ylabel("Probability of Being Late")
plt.title("Probability of Rita Being Late Depending on Departure Time")
plt.grid(True)
plt.legend()

# Save the graph
plt.savefig("rita_lateness_graph.png")
print("Plot saved as 'rita_lateness_graph.png'")