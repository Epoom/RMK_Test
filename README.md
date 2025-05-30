# **Will Rita make it to work?**
## Table of contents
🤔 [What is this and what does it do?](#what-is-this-and-what-does-it-do)<br/>
❓ [How does it work?](#how-does-it-work)<br/>
📡 [How does GPS tracking work?](#how-does-gps-tracking-work)<br/>
🤓 [Testing the tool](#testing-the-tool)<br/>
🤝 [Creator](#creator)

## What is this and what does it do?
This Python script simulates Rita's daily commute from Zoo to Toompark using Tallinn city bus number 8. The goal is to estimate:
* Rita's arrival time at the office
* The probability that she will be late for her 9:05 AM meeting

Powered by real-time bus tracking, the tool fetches live bus positions from the Tallinn transport feed (gps.txt) every time it runs.
## How does it work?
1. Fetches live bus tracking data from https://transport.tallinn.ee/gps.txt.

2. Filters for Bus 8 and selects the closest bus near Zoo based on real-time GPS location.

3. Estimates arrival time at Zoo dynamically based on the bus speed and distance.

4. Simulates Rita’s commute:
	* Adds 300 seconds for Rita’s walk from home to the zoo bus stop.
	* Finds the next available bus.
	* Travel from Zoo to Toompea is fixed at an estimated duration of 10 minutes.
	* Adds 240 seconds for the walk from Toompark to the office.

5. Determines the probability of Rita being late based on the simulation.

6. Plots a graph showing the probability of lateness based on departure times.

## How does GPS tracking work?
1. The tool fetches real-time GPS data from Tallinn’s open transport system (https://transport.tallinn.ee/gps.txt). This dataset updates every 5 seconds.

2. Once the data is retrieved, the script removes all irrelevant transport data and keeps only Bus 8 so that we only have live positions for buses running on Route 8.

3. Once we have all Bus 8 vehicles, the tool determines which one is nearest to the Zoo stop by computing real-time distance from each bus to Zoo using latitude/longitude and selecting the bus with the shortest distance as the next arriving bus.

4. Once the closest Bus 8 is identified, it calculate how long it will take to reach Zoo based on speed by taking the distance from Zoo to the bus, dividing it by bus speed to estimate arrival time.

5. Once Rita boards the bus, she needs to travel from Zoo to Toompea. We assume a fixed average travel time of 10 minutes based on bus data.

## Testing the tool?
1. Install Python and required libraries

	Ensure you have Pyhton installed.

	Run the following command to install dependencies:
	```bash
	pip install pandas numpy matplotlib geopy
	```
2. Run the script

	Open a terminal in the project folder and execute:

	```bash
	python simulate_commute.py
	```

The script will:
* Fetch live bus data dynamically.
* Simulate Rita’s commute for different departure times.
* Save a CSV file (rita_lateness_results.csv) showing whether she is late.
* Generate a graph (rita_lateness_graph.png) displaying the probability of being late.

## Creator
This tool was developed by Egert-Yako Poom