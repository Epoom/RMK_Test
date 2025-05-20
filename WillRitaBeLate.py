import pandas as pd

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

# === Testing ===
test_times = [
    time_to_seconds("08:00"),  # Should return the first bus after 08:00.
    time_to_seconds("08:30"),  # Should return the next bus after 08:30.
    time_to_seconds("08:45"),  # Should return the next bus after 08:45.
    time_to_seconds("09:00"),  # Should return the next bus after 09:00.
    time_to_seconds("10:00")   # Rita will be late to meeting.
]

print("\nTesting get_next_bus function:")

for test_time in test_times:
    bus, wait_time = get_next_bus(test_time, schedule_df)
    if bus:
        print(f"At {seconds_to_time(test_time)}, next bus at {seconds_to_time(bus['ZooDepartureSec'])}, "
              f"waiting {wait_time} sec, arriving at {seconds_to_time(bus['ToomparkArrivalSec'])}")
    else:
        print(f"At {seconds_to_time(test_time)}, Rita is late!")