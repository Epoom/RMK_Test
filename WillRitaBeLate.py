import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def time_to_seconds(t_str):
    """
    Convert a time string 'HH:MM' to seconds since midnight.
    """
    hour, minute = map(int, t_str.strip().split(":"))
    return hour * 3600 + minute * 60

def seconds_to_time(sec):
    """
    Convert seconds since midnight to HH:MM format.
    """
    hour = int(sec // 3600)
    minute = int((sec % 3600) // 60)
    return f"{hour:02d}:{minute:02d}"

# === Read and Process the Bus Schedule ===

schedule_df = pd.read_csv("bus_times.csv", skipinitialspace=True)
schedule_df["ZooDepartureSec"] = schedule_df["ZooDepartureTime"].apply(time_to_seconds)
schedule_df["ToomparkArrivalSec"] = schedule_df["ToomparkArrivalTime"].apply(time_to_seconds)
schedule_df.sort_values("ZooDepartureSec", inplace=True)

# print("Processed Bus Schedule:") #
# print(schedule_df[["ZooDepartureTime", "ToomparkArrivalTime", "ZooDepartureSec", "ToomparkArrivalSec"]]) #

def get_next_bus(t_arrival_stop, bus_schedule):
    """
    Given the time (in seconds) when Rita arrives at the bus stop,
    return a tuple (bus, wait_time) where:
      - bus is a row (as dict) from the bus schedule
      - wait_time is the seconds Rita waits for that bus.
    If no bus is available, or bus time is past 09:00, returns (None, float("inf")).
    """
    for _, row in bus_schedule.iterrows():
        if row["ZooDepartureSec"] >= t_arrival_stop:
            wait_time = row["ZooDepartureSec"] - t_arrival_stop
            return row.to_dict(), wait_time
    return None, float("inf")

# === Simulating Departure Times ===

# Define constants
MEETING_TIME = time_to_seconds("09:05")
HOME_TO_BUS_STOP = 300  # 300 seconds = 5 minutes
BUS_STOP_TO_MEETING = 240  # 240 seconds = 4 minutes

# Simulate Rita leaving home at different times
departure_times = np.arange(time_to_seconds("07:30"), time_to_seconds("09:00"), 60)  # Every minute
results = []

for dep_time in departure_times:
    arrival_at_bus_stop = dep_time + HOME_TO_BUS_STOP
    bus, wait_time = get_next_bus(arrival_at_bus_stop, schedule_df)

    if bus:
        arrival_at_meeting = bus["ToomparkArrivalSec"] + BUS_STOP_TO_MEETING
        late = arrival_at_meeting > MEETING_TIME
    else:
        late = True  # No available bus means Rita is late

    results.append({"DepartureTime": seconds_to_time(dep_time), "Late": late})

# Convert results into a DataFrame for analysis
results_df = pd.DataFrame(results)
# Modify the results format
results_df["Late"] = results_df["Late"].map({True: "Late", False: "Not Late"})

# Print updated results
print(results_df)

# === Configure and save results ===

results_df.to_csv("rita_lateness_results.csv", index=False)

print("Results successfully saved to 'rita_lateness_results.csv'")

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

# Save the graph instead of displaying
plt.savefig("rita_lateness_plot.png")
print("Plot saved as 'rita_lateness_plot.png'")



