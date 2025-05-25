import pandas as pd
import numpy as np

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

# === Save results to a CSV file ===
results_df.to_csv("rita_lateness_results.csv", index=False)

print("Results successfully saved to 'rita_lateness_results.csv'")

