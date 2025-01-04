import json
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Define POIs
pois = [
    {"poi_id": 1, "poi_name": "Selfridges", "poi_category": "Department Store", "poi_latitude": 51.5147, "poi_longitude": -0.1528},
    {"poi_id": 2, "poi_name": "Fortnum & Mason", "poi_category": "Luxury Department Store", "poi_latitude": 51.5093, "poi_longitude": -0.1376},
    {"poi_id": 3, "poi_name": "Harrods", "poi_category": "Luxury Department Store", "poi_latitude": 51.4994, "poi_longitude": -0.1635},
    {"poi_id": 4, "poi_name": "Liberty London", "poi_category": "Luxury Goods", "poi_latitude": 51.5133, "poi_longitude": -0.1407},
    {"poi_id": 5, "poi_name": "The Buckingham Palace Shop", "poi_category": "Souvenir Shop", "poi_latitude": 51.5014, "poi_longitude": -0.1448},
    {"poi_id": 6, "poi_name": "Hamleys", "poi_category": "Toy Store", "poi_latitude": 51.5129, "poi_longitude": -0.1404},
    {"poi_id": 7, "poi_name": "Apple Regent Street", "poi_category": "Electronics", "poi_latitude": 51.5146, "poi_longitude": -0.1410},
    {"poi_id": 8, "poi_name": "Burberry Regent Street", "poi_category": "Fashion", "poi_latitude": 51.5139, "poi_longitude": -0.1406},
    {"poi_id": 9, "poi_name": "M&M’s World London", "poi_category": "Specialty Store", "poi_latitude": 51.5115, "poi_longitude": -0.1316},
    {"poi_id": 10, "poi_name": "Covent Garden Market", "poi_category": "Shopping District", "poi_latitude": 51.5110, "poi_longitude": -0.1236}
]

demographics = ["Young M", "Young F", "Couples", "Family with C","Retiree"]
lifestyles = ["Affluent Achievers", "Suburban Comfort", "Urban Professionals", "Peri-Urban Residents"]

# Generate traffic data
start_date = datetime(2024, 6, 1)  # Start date: 1-Jun-2024
end_date = start_date + timedelta(days=90)  # 90 days from start date
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

# UK public holidays in the period (for 2024)
uk_public_holidays = [
    datetime(2024, 8, 26)  # Late Summer Bank Holiday
]

def determine_day_type(single_date):
    if single_date.weekday() >= 5 or single_date in uk_public_holidays:
        return 'Weekend'
    return 'Weekday'

def generate_daily_traffic(day_type):
    # Base traffic volume varies by POI category
    base_traffic = random.randint(500, 3000)
    # Weekday multiplier
    multiplier = 1.2 if day_type == 'Weekend' else 1.0

    # Randomized male/female split
    #male_percentage = random.uniform(0.45, 0.55)
    #female_percentage = 1 - male_percentage

    total_visitor_count = int(base_traffic * multiplier)
    #male_traffic = int(total_visitor_count * male_percentage)
    #female_traffic = total_visitor_count - male_traffic
    
    # Generate a random distribution for the demographics and lifestyles
    demographic_distribution = np.random.dirichlet(np.ones(len(demographics)), size=1)[0]
    lifestyles_distribution  = np.random.dirichlet(np.ones(len(lifestyles)), size=1)[0]
    
    # Scale the distribution to match the cumulative_visitors count
    demographic_visitor_count = {
        demographics[i]: int(demographic_distribution[i] * total_visitor_count)
        for i in range(len(demographics))
    }
    #print(demographic_visitor_count)
    lifestyles_visitor_count = {
        lifestyles[i]: int(lifestyles_distribution[i] * total_visitor_count)
        for i in range(len(lifestyles))
    }

    return total_visitor_count, demographic_visitor_count, lifestyles_visitor_count

# Create dataset
traffic_data_csv = []
traffic_data_json = []
for poi in pois:
    for single_date in date_range:
        day_type = determine_day_type(single_date)
        total, demographic_visitor_count, lifestyles_visitor_count = generate_daily_traffic(day_type)
        traffic_data_json.append({
            "poi_id": poi["poi_id"],
            "poi_name": poi["poi_name"],
            "date": single_date.strftime("%Y-%m-%d"),
            "total_visitor_count": total,
            "demographic_visitor_count": [demographic_visitor_count],
            "lifestyles_visitor_count": [lifestyles_visitor_count],
            "day_type": day_type
        })

        # Flatten the data for CSV format
        # Iterate over demographic categories and store them as rows
        for category, count in demographic_visitor_count.items():
            traffic_data_csv.append({
                "poi_id": poi["poi_id"],
                "poi_name": poi["poi_name"],
                "date": single_date.strftime("%Y-%m-%d"),
                "category": category,
                "visitor_count": count,
                "day_type": day_type
            })
        
        # Iterate over lifestyle categories and store them as rows
        for category, count in lifestyles_visitor_count.items():
            traffic_data_csv.append({
                "poi_id": poi["poi_id"],
                "poi_name": poi["poi_name"],
                "date": single_date.strftime("%Y-%m-%d"),
                "category": category,
                "visitor_count": count,
                "day_type": day_type
            })
        #demographic_category, lifestyle_category, visitor_count

# Convert to DataFrame
traffic_df = pd.DataFrame(traffic_data_json)
print(traffic_df.head(0))

# Save the DataFrame as JSON
json_path = "poi_traffic_data.json"
traffic_data_json = traffic_df.to_dict(orient="records")  # Convert to list of dictionaries

# Save to CSV
traffic_df = pd.DataFrame(traffic_data_csv)
traffic_df.to_csv("poi_traffic_data.csv", index=False)

# Write JSON to file
with open(json_path, "w") as json_file:
    json.dump(traffic_data_json, json_file, indent=4)

# Plot using Plotly
traffic_df['date'] = pd.to_datetime(traffic_df['date'])

# Dropdown menu for POI selection
poi_options = traffic_df['poi_name'].unique()

fig = go.Figure()

def update_figure(selected_poi):
    filtered_df = traffic_df[traffic_df['poi_name'] == selected_poi]
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=filtered_df['date'], y=filtered_df['total_visitor_count'],
        mode='lines', name='Total Traffic',
        line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=filtered_df['date'], y=filtered_df['male_traffic'],
        mode='lines', name='Male Traffic',
        line=dict(color='green')
    ))
    fig.add_trace(go.Scatter(
        x=filtered_df['date'], y=filtered_df['female_traffic'],
        mode='lines', name='Female Traffic',
        line=dict(color='red')
    ))

    # Update layout with slider and titles
    fig.update_layout(
        title=f"Traffic Volume Over Time for {selected_poi} (Total, Male, Female)",
        xaxis_title="Date",
        yaxis_title="Traffic Volume",
        legend_title="Traffic Type",
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date",
            tickformat="%Y-%m-%d"  # Format ticks as days
        )
    )
    return fig

# Create an interactive dropdown menu
from ipywidgets import widgets
from IPython.display import display

dropdown = widgets.Dropdown(
    options=poi_options,
    value=poi_options[0],
    description='Select POI:'
)

def on_dropdown_change(change):
    if change['type'] == 'change' and change['name'] == 'value':
        updated_fig = update_figure(change['new'])
        updated_fig.show()

dropdown.observe(on_dropdown_change)
display(dropdown)

# Show initial figure
initial_fig = update_figure(poi_options[0])
initial_fig.show()

print("Traffic data generated and visualized with POI selection.")
