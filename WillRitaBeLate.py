import pandas as pd

def time_to_seconds(t_str):
    """
    Convert a time string 'HH:MM' to seconds since midnight.
    """
    hour, minute = map(int, t_str.strip().split(":"))
    return hour * 3600 + minute * 60

# Read the bus schedule
schedule_df = pd.read_csv("bus_times.csv", skipinitialspace=True)
schedule_df["ZooDepartureSec"] = schedule_df["ZooDepartureTime"].apply(time_to_seconds)
schedule_df["ToomparkArrivalSec"] = schedule_df["ToomparkArrivalTime"].apply(time_to_seconds)
schedule_df.sort_values("ZooDepartureSec", inplace=True)

print("Processed Bus Schedule:")
print(schedule_df[["ZooDepartureTime", "ToomparkArrivalTime", "ZooDepartureSec", "ToomparkArrivalSec"]])