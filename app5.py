import math
import redis
import json
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from dash import dash, Dash, dcc, html, no_update, callback_context
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from Geo_Coordinates_Data import westminster_shops_pois, westminster_shops_pois_df, westminster_towers

import plotly.express as px

############################## INITILIZATIONS
#Define global datasets
poi_visitors_history = {
    "timestamp": [],
    "poi_visitors": []  # Each entry will be a DataFrame
}
poi_visitors_history_df = pd.DataFrame()

demographics = ["Young M", "Young F", "Couples", "Family with C","Retiree"]
lifestyles = ["Affluent Achievers", "Suburban Comfort", "Urban Professionals", "Peri-Urban Residents"]

# Define colors similar to dark24 for 3d surface Charts
dark24_colorscale = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

#Get the history data
# Convert to DataFrame
#traffic_df = pd.read_csv("./data/poi_traffic_data.csv")
with open("./data/poi_traffic_data.json", "r") as file:
    json_data = json.load(file)

# Convert to DataFrame
traffic_df = pd.json_normalize(json_data)

#This is the radius in meters from the POI to considers all the towers in range of this POI
proximity_dist_m = 500

#Initiate Redis for retrieve  messages captured and stored by Kafka Consumer
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Start the consumer in a background thread
updated_tower_connections = {tower_id: 0 for tower_id in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}

############################## FUNCTIONS
# Haversine formula to calculate geographic distance between towers and POIs
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c * 1000  # Convert to meters
    
#Functio to retrieve messages from Redis
def updated_tower_connections_from_redis():
    messages = []
    while redis_client.llen("tower_messages") > 0:  # Check list length
        msg = redis_client.lpop("tower_messages")  # Remove the first message
        if msg:
            messages.append(json.loads(msg))
    
    for event in messages:
        tower_id = event['tower_id']
        #Net connections = connections - disconnections
        updated_tower_connections[tower_id] =  (event['connections'] - event['dis_connections'])
    
    max_visit_count=max(updated_tower_connections.values()) if updated_tower_connections else 1
    max_visit_count = max_visit_count if max_visit_count > 0 else 1

    tower_visitors = []
    for tower_id, count in updated_tower_connections.items():
        lat = westminster_towers[tower_id-1]["latitude"]
        long = westminster_towers[tower_id-1]["longitude"]

        tower_visitors.append({
        "tower_id": tower_id,
        "latitude": lat,
        "longitude": long,
        "count": count,
        "marker_size": 10 + int((20 * count / max_visit_count))
        })

    return tower_visitors

# Function to get the traffic at POI by calculating the traffic at the towers near-by to the POIs by 500m
def get_poi_traffic(tower_visitors):
    global poi_visitors_history_df

    poi_visitors = []
    for poi in westminster_shops_pois:
        poi_lat, poi_lon = poi['poi_latitude'], poi['poi_longitude']
        nearby_towers = tower_visitors[
            tower_visitors.apply(lambda x: haversine(poi_lat, poi_lon, x['latitude'], x['longitude']) <= proximity_dist_m, axis=1)
        ]
        #nearby_users = user_df[user_df['tower_id'].isin(nearby_towers['tower_id'])]
        #visit_counts[poi['poi_id']] = len(nearby_users) + np.random.randint(1,10)
        cumulative_visitors = 0
        avg_dwell_time = random.randint(300, 1800) #5 mins to 30 mins
        poi_nearby_towers = ""
        for index, tower in nearby_towers.iterrows():
            cumulative_visitors +=  tower['count']
            if poi_nearby_towers == "":
                poi_nearby_towers = str(int(tower['tower_id']))  # Just add the first tower ID
            else:
                poi_nearby_towers += ', ' + str(int(tower['tower_id']))
        
        
        # Generate a random distribution for the demographics and lifestyles
        demographic_distribution = np.random.dirichlet(np.ones(len(demographics)), size=1)[0]
        lifestyles_distribution  = np.random.dirichlet(np.ones(len(lifestyles)), size=1)[0]
        
        # Scale the distribution to match the cumulative_visitors count
        demographic_visitor_count = {
            demographics[i]: int(demographic_distribution[i] * cumulative_visitors)
            for i in range(len(demographics))
        }
        lifestyles_visitor_count = {
            lifestyles[i]: int(lifestyles_distribution[i] * cumulative_visitors)
            for i in range(len(lifestyles))
        }

        poi_visitors.append({
            "poi_id": poi['poi_id'],
            "poi_name": poi['poi_name'],
            "poi_latitude": poi_lat,
            "poi_longitude": poi_lon,
            "poi_visitor_count": cumulative_visitors,
            "poi_avg_dwell_time": avg_dwell_time,
            "poi_nearby_towers": poi_nearby_towers,
            "demographic_distribution": demographic_visitor_count,
            "lifestyles_distribution": lifestyles_visitor_count
        })
    
    poi_visitors_history["timestamp"].append(datetime.now())
    poi_visitors_history["poi_visitors"].append(poi_visitors)

    # Convert to DataFrame
    poi_visitors_history_df = pd.DataFrame(poi_visitors_history)
    # Sort the DataFrame by timestamp in descending order
    poi_visitors_history_df.sort_values(by="timestamp", ascending=False, inplace=True)

    # Keep only the most recent 20 rows
    poi_visitors_history_df = poi_visitors_history_df.head(20)

    # Reset the index after slicing
    poi_visitors_history_df.reset_index(drop=True, inplace=True)

    return poi_visitors

#Update history  charts - for demography and lifestyles
def update_history_charts(filtered_df, selected_poi):
    global demographics
    global lifestyles

    # Create an empty list to hold the long-format rows
    long_format_demography = []
    long_format_lifestyle = []

    # Loop over each row in the original DataFrame
    for _, row in filtered_df.iterrows():
        # Get the date
        date = row['date']
        
        # Extract the demographic counts as a dictionary
        demographic_counts = row['demographic_visitor_count'][0]
        lifestyle_counts = row['lifestyles_visitor_count'][0]

        # For each demographic category and its count, create a new row
        for category, count in demographic_counts.items():
            long_format_demography.append([date, category, count])

        # For each demographic category and its count, create a new row
        for category, count in lifestyle_counts.items():
            long_format_lifestyle.append([date, category, count])

    # Convert the list of rows into a DataFrame
    long_format_demography_df = pd.DataFrame(long_format_demography, columns=['date', 'demographic_category', 'visitor_count'])
    long_format_lifestyle_df =  pd.DataFrame(long_format_lifestyle, columns=['date', 'lifestyle_category', 'visitor_count'])

    # Create the stacked bar chart - demography
    fig1 = go.Figure()

    # Add a trace for each demographic category
    for demography in demographics:
        # Filter data for the current category
        demography_data = long_format_demography_df[long_format_demography_df['demographic_category'] == demography]
        # Create the trace for this demographic category
        fig1.add_trace(go.Bar(
            x=demography_data['date'], 
            y=demography_data['visitor_count'], 
            name=demography
        ))

    # Update layout
    fig1.update_layout(
        title=f"Visitor Demographics Over Time for {selected_poi}",
        paper_bgcolor="#2e2e2e",  # Dark gray background
        plot_bgcolor="#2e2e2e",   # Dark gray plot area
        font=dict(color="white"), # White font for all text
        title_font=dict(color="#add8e6"),  # Light blue for chart title
        #hover_data=['lifeExp', 'gdpPercap'], color='country',
        xaxis_title="Date",
        yaxis_title="Visitor Count",
        barmode="stack",                # Stack the bars
        legend_title="Demographics",
        #xaxis=dict(rangeslider=dict(visible=True), type="date", tickformat="%Y-%m-%d")
        xaxis=dict(tickangle=-45, rangeslider=dict(visible=True), type="date", tickformat="%Y-%m-%d"),  # Ensure dates are shown properly on the x-axis
    )

    # Create the stacked bar chart - Lifestyle
    fig2 = go.Figure()

    # Add a trace for each demographic category
    for lifestyle in lifestyles:
        # Filter data for the current category
        lifestyle_data = long_format_lifestyle_df[long_format_lifestyle_df['lifestyle_category'] == lifestyle]
        # Create the trace for this demographic category
        fig2.add_trace(go.Bar(
            x=lifestyle_data['date'], 
            y=lifestyle_data['visitor_count'], 
            name=lifestyle
        ))

    # Update layout
    fig2.update_layout(
        title=f"Visitor Lifestyles Over Time for {selected_poi}",
        paper_bgcolor="#2e2e2e",  # Dark gray background
        plot_bgcolor="#2e2e2e",   # Dark gray plot area
        font=dict(color="white"), # White font for all text
        title_font=dict(color="#add8e6"),  # Light blue for chart title
        #hover_data=['lifeExp', 'gdpPercap'], color='country',
        xaxis_title="Date",
        yaxis_title="Visitor Count",
        barmode="stack",                # Stack the bars
        legend_title="Lifestyles",
        xaxis=dict(tickangle=-45, rangeslider=dict(visible=True), type="date", tickformat="%Y-%m-%d"),  # Ensure dates are shown properly on the x-axis
    )
    
    return fig1, fig2

#Update real-time surface charts for each POI - demography and lifestyles
def update_poi_surface_charts(selected_poi):
    global demographics
    global lifestyles
    global poi_visitors_history_df

    if not selected_poi:  # Handle case where no POI is selected
        return go.Figure()

    #Plotting Density by POI for Demographics (Real-Time)
    x_vals = poi_visitors_history_df["timestamp"].dt.strftime("%H:%M:%S")  # Unique timestamps formatted as HH:MM:SS
    y_vals = demographics
    z_vals = []

    # Populate Z-axis grid
    for _, timestamp in enumerate(x_vals):  # Loop through timestamps
        # Access the corresponding poi_visitors list for the timestamp
        poi_list = poi_visitors_history_df.loc[poi_visitors_history_df["timestamp"].dt.strftime("%H:%M:%S") == timestamp, "poi_visitors"].iloc[0]
        # Find the selected POI in each timestamp's data
        for poi_data in poi_list:
            if poi_data:
                if poi_data['poi_name'] == selected_poi:
                    # Use demographic distribution for the selected POI
                    z_vals.append(
                        [poi_data["demographic_distribution"].get(demo, 0) for demo in demographics]
                    )

    # Create the 3D surface chart
    fig1 = go.Figure(data=[
        go.Surface(
            z=z_vals,  # Visitor counts (Z-axis)
            x=x_vals,  # Time (X-axis)
            y=y_vals,  # Demographics (Y-axis)
            colorscale="Viridis",
            showscale=False
        )
    ])

    # Update layout
    fig1.update_layout(
        title=f"Demographic Density for {selected_poi}",
        paper_bgcolor="#383a3b",  # Dark gray background
        font=dict(color="white"), # White font for all text
        title_font=dict(color="#add8e6"),  # Light blue for chart title
        scene=dict(
            xaxis_title="Time (HH:MM)",
            yaxis_title="Demographics",
            zaxis_title="Visitor Count"
        )
    )

    #Plotting Density by POI for Lifestyle (Real-Time)
    y_vals = lifestyles
    z_vals = []

    # Populate Z-axis grid
    for _, timestamp in enumerate(x_vals):  # Loop through timestamps
        # Access the corresponding poi_visitors list for the timestamp
        poi_list = poi_visitors_history_df.loc[poi_visitors_history_df["timestamp"].dt.strftime("%H:%M:%S") == timestamp, "poi_visitors"].iloc[0]
        # Find the selected POI in each timestamp's data
        for poi_data in poi_list:
            if poi_data:
                if poi_data['poi_name'] == selected_poi:
                    # Use lifestyles distribution for the selected POI
                    z_vals.append(
                        [poi_data["lifestyles_distribution"].get(lifes, 0) for lifes in lifestyles]
                    )

    # Create the 3D surface chart
    fig2 = go.Figure(data=[
        go.Surface(
            z=z_vals,  # Visitor counts (Z-axis)
            x=x_vals,      # Time (X-axis)
            y=y_vals,    # Demographics (Y-axis)
            colorscale="Inferno",
            showscale=False
        )
    ])

    # Update layout
    fig2.update_layout(
        title=f"Lifestyles Density for {selected_poi}",
        paper_bgcolor="#383a3b",  # Dark gray background
        font=dict(color="white"), # White font for all text
        title_font=dict(color="#add8e6"),  # Light blue for chart title
        scene=dict(
            xaxis_title="Time (HH:MM)",
            yaxis_title="Lifestyles",
            zaxis_title="Visitor Count"
        )
    )

    return fig1, fig2

############################## APP LAYOUT
# Visualization using Dash
app5 = Dash(__name__)

app5.layout = html.Div([
    html.Div(  # Wrapper Div with className
        className="container",
        children=[
            # Header
            html.Header("Real-Time Point of Interest Insights"),

            # Layout line 1 - City Map with POIs and real-time visitor count
            html.Div(
                className="map",
                children=[
                    dcc.Graph(id="live-map", style={"height": "350px"})
                ]
            ),

            #Layout line 2 - 3d surface - density by POI, dwell time by POI
            html.Div(
                className="chart-row-even", 
                children=[
                    # Density by POI
                    html.Div(
                        className="chart-container",
                        children=[
                            html.H4("Visitor Density by POI", className="chart-title"),
                            dcc.Graph(id="density-by-poi-3d", className="chart chart-3d"),
                        ]
                    ),
                    # Dwell Time by POI
                    html.Div(
                        className="chart-container",
                        children=[
                            html.H4("Dwell Time by POI", className="chart-title"),
                            dcc.Graph(id="dwelltime-by-poi-3d", className="chart chart-3d"),
                        ]
                    ),
                ]
            ),

            # Layout line 3 - Dropdown for POI selection
            html.Div(
                className="dropdown-container",
                children=[
                    html.Div(
                        className="dropdown-row",
                        children=[
                            dcc.Dropdown(
                                id='poi-dropdown',
                                options=[{'label': poi['poi_name'], 'value': poi['poi_name']} for poi in westminster_shops_pois],
                                value=westminster_shops_pois[0]['poi_name'],  # Default to the first POI
                                placeholder="Select a POI",
                                className="dropdown",
                            ),
                            html.Span(
                                children=[
                                    html.P(id="poi-details", children=[html.Strong("POI Details: "), "Loading ..."]),
                                ],
                                className="details"
                            )
                        ]
                    )
                ]
            ),

            # Layout line 4 - POI Demographic: Historical line chart and 3D surface chart
            html.Div(
                className="chart-row-uneven-left",
                children=[
                    dcc.Graph(id="poi-historical-traffic-demography", className="chart line-chart"),
                    dcc.Graph(id="3d-surface-poi-demography", className="chart surface-chart"),
                ]
            ),

            # Layout line 5 - POI Socio-Economic: historical line chart and 3D surface chart
            html.Div(
                className="chart-row-uneven-right",
                children=[
                    dcc.Graph(id="3d-surface-poi-lifestyle", className="chart surface-chart"),
                    dcc.Graph(id="poi-historical-traffic-lifestyle", className="chart line-chart"),
                ]
            ),
        ]
    ),

    # Interval for real-time updates
    dcc.Interval(
        id='interval-component',
        interval=5000,  # Update every 5 seconds
        n_intervals=0
    )
])

############################## APP CALLBACKS
# Callback to update the map
@app5.callback(
    Output('live-map', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_map(n):
    tower_visitors = updated_tower_connections_from_redis()  # Fetch and clear messages from Redis
    tower_visitors = pd.DataFrame(tower_visitors)

    #Get the traffic at POIs
    poi_visitors = get_poi_traffic(tower_visitors)

    # Calculate max and min
    poi_visitors = pd.DataFrame(poi_visitors)

    max_visit_count = poi_visitors['poi_visitor_count'].max()  # Get max visitor count
    min_visit_count = poi_visitors['poi_visitor_count'].min()  # Get min visitor count
    # Add the 'marker_size' column based on the formula
    poi_visitors['marker_size'] = 20 + ((20 * poi_visitors['poi_visitor_count']) / max_visit_count)

    # Normalize the marker sizes to use for color mapping (optional)
    # This makes the colors proportional to the size
    normalized_colors = (poi_visitors['marker_size'] - min_visit_count) / (max_visit_count - min_visit_count)

    tower_markers = go.Scattermapbox(
        lat=tower_visitors['latitude'],
        lon=tower_visitors['longitude'],
        mode='markers',
        marker=dict(
            size=10,
            color='red',
            opacity=0.5
        ),
        text=[f"Tower {row['tower_id']}: {row['count']}" for _, row in tower_visitors.iterrows()]
    )

    poi_markers = go.Scattermapbox(
        lat=poi_visitors['poi_latitude'],
        lon=poi_visitors['poi_longitude'],
        mode='markers', #mode='markers+text',
        marker=dict(
            size=poi_visitors['marker_size'],
            color=normalized_colors,            # Colors mapped to marker sizes
            #color='red',
            #colorscale='Viridis_r',               # Choose a colorscale (e.g., 'Viridis', 'Cividis', 'Plasma', 'Inferno', 'Magma', 'Blues') _r is reversed
            colorscale='IceFire',
            opacity=0.9,
            showscale=True
        ),
        text=[f"{row['poi_name']}: {row['poi_visitor_count']}" for _, row in poi_visitors.iterrows()]
        #name=[f"{row['poi_name']}" for _, row in poi_visitors.iterrows()]
    )
    
    fig = go.Figure()
    fig.add_trace(poi_markers)
    fig.add_trace(tower_markers)
    fig.update_layout(
        mapbox=dict(
            style='open-street-map', #carto-positron, open-street-map
            center=dict(lat=51.5074, lon=-0.1278),
            zoom=12
        ),
        #title="POI Map",
        margin=dict(l=5, r=0, t=5, b=5)
    )
    return fig

# Callback to Update Traffic Chart Based on Dropdown Selection or Map Click
@app5.callback(
    [Output('poi-details', 'children'),
     Output('poi-historical-traffic-demography', 'figure'),
     Output('3d-surface-poi-demography', 'figure'),
     Output('3d-surface-poi-lifestyle', 'figure'),
     Output('poi-historical-traffic-lifestyle', 'figure')],
    [Input('poi-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_traffic_chart(selected_poi, n_intervals):
# Get the trigger that caused the callback
    fig1 = go.Figure()
    ctx = callback_context

    # Check if a POI is clicked in the dropdown
    if not selected_poi:
        print("No POI information ", ctx.triggered)
        return no_update, no_update, no_update, no_update, no_update   # Exit without updating the figure

    # Check which input triggered the callback
    poi_details = westminster_shops_pois_df[westminster_shops_pois_df["poi_name"] == selected_poi]
    selected_poi_details = f"{poi_details['poi_name'].iloc[0]}: {poi_details['poi_description'].iloc[0]}. Located at Lat: {poi_details['poi_latitude'].iloc[0]} Long: {poi_details['poi_longitude'].iloc[0]}"

    if ctx.triggered:
        triggered_input = ctx.triggered[0]['prop_id']
        event = "", ctx.triggered, selected_poi
        if triggered_input == "interval-component.n_intervals":
            #Update surface charts
            #print("Interval: ", n_intervals, " ", selected_poi)
            fig2, fig3 = update_poi_surface_charts(selected_poi)
            return selected_poi_details, no_update, fig2, fig3, no_update  # only update the surface charts
    else:
        event = "Callback triggered with no context (initial load) ", ctx.triggered, selected_poi
    
    #Update line charts
    filtered_df = traffic_df.loc[traffic_df['poi_name'] == selected_poi]
    fig1, fig4 = update_history_charts(filtered_df, selected_poi)
    return selected_poi_details, fig1, no_update, no_update, fig4

# Callback to update the dropdown value based on map click
@app5.callback(
    Output('poi-dropdown', 'value'),  # Update the dropdown's selected value
    Input('live-map', 'clickData')   # Listen for clicks on the map
)
def update_dropdown_on_map_click(click_data):
    if click_data:  # If a POI is clicked on the map
        clicked_poi_name = click_data['points'][0]['text'].split(":")[0]
        if clicked_poi_name in [poi['poi_name'] for poi in westminster_shops_pois]:
            return clicked_poi_name
    return no_update  # Keep the current selection if no clickData

#Callback to refresh Line 2 - 3d Surface charts for density and dwell times by POI
@app5.callback(
    [Output('density-by-poi-3d', 'figure'),
    Output('dwelltime-by-poi-3d', 'figure')],
    Input('interval-component', 'n_intervals')

)
def update_poi_plots_line2(n_intervals):
    global poi_visitors_history_df

    # Extracting and formatting data for the surface plot
    x_vals = poi_visitors_history_df["timestamp"].dt.strftime("%H:%M:%S")  # Unique timestamps formatted as HH:MM:SS
    y_vals = sorted({poi["poi_name"] for poi_list in poi_visitors_history_df["poi_visitors"] for poi in poi_list})  # Unique POI names
    z_vals = np.zeros((len(y_vals), len(x_vals)))  # Initialize Z-axis (visitor counts)

    # Generate tick values as 10 evenly spaced indices
    tick_indices = np.linspace(0, len(x_vals) - 1, 10, dtype=int)

    #Plotting Density by POI
    # Populate Z-axis grid
    for j, timestamp in enumerate(x_vals):  # Loop through timestamps
        # Access the corresponding poi_visitors list for the timestamp
        poi_list = poi_visitors_history_df.loc[poi_visitors_history_df["timestamp"].dt.strftime("%H:%M:%S") == timestamp, "poi_visitors"].iloc[0]
        for poi in poi_list:
            i = y_vals.index(poi["poi_name"])  # Find row index for the POI name
            z_vals[i, j] = poi["poi_visitor_count"]  # Assign visitor count

    # Create 3D surface chart
    fig1 = go.Figure()

    fig1.add_trace(go.Surface(
        z=z_vals,
        x=np.arange(len(x_vals)),  # Indices for X-axis
        y=np.arange(len(y_vals)),  # Indices for Y-axis
        colorscale='IceFire', #"Dark24", #, Viridis, IceFire
        showscale=True
    ))

    # Update layout with proper labels
    fig1.update_layout(
        #title="3D Surface Chart: Visitor Count by POI and Time",
        paper_bgcolor="#757575",  # Dark gray background
        font=dict(color="white"), # White font for all text
        title_font=dict(color="#add8e6"),  # Light blue for chart title
        scene=dict(
            xaxis=dict(
                backgroundcolor="rgb(200, 200, 230)",
                title="Time (HH:MM:SS)",
                #tickvals=np.arange(len(x_vals)), #tick_indices
                tickvals=tick_indices,
                ticktext=x_vals.tolist()  # Use formatted timestamps
            ),
            yaxis=dict(
                backgroundcolor="rgb(200, 200, 230)",
                title="POI Name",
                tickvals=np.arange(len(y_vals)),
                ticktext=y_vals  # Use POI names
            ),
            zaxis=dict(
                backgroundcolor="rgb(40, 44, 52)",
                title="Visitor Count")
        ),
        width=800,
        margin=dict(r=10, l=10, b=10, t=10)
    )

    #Plotting Dwelltime by POI
    # Populate Z-axis grid
    for j, timestamp in enumerate(x_vals):  # Loop through timestamps
        # Access the corresponding poi_visitors list for the timestamp
        poi_list = poi_visitors_history_df.loc[poi_visitors_history_df["timestamp"].dt.strftime("%H:%M:%S") == timestamp, "poi_visitors"].iloc[0]
        for poi in poi_list:
            i = y_vals.index(poi["poi_name"])  # Find row index for the POI name
            z_vals[i, j] = poi["poi_avg_dwell_time"]  # Assign visitor count

    # Create 3D surface chart
    fig2 = go.Figure()

    fig2.add_trace(go.Surface(
        z=z_vals,
        x=np.arange(len(x_vals)),  # Indices for X-axis
        y=np.arange(len(y_vals)),  # Indices for Y-axis
        #colorscale="Inferno",
        showscale=True
    ))

    # Update layout with proper labels
    fig2.update_layout(
        #title="3D Surface Chart: Visitor Count by POI and Time",
        paper_bgcolor="#757575",  # Dark gray background
        font=dict(color="white"), # White font for all text
        title_font=dict(color="#add8e6"),  # Light blue for chart title
        scene=dict(
            xaxis=dict(
                backgroundcolor="rgb(255, 182, 170)",
                title="Time (HH:MM:SS)",
                #tickvals=np.arange(len(x_vals)),
                tickvals=tick_indices,
                ticktext=x_vals.tolist()  # Use formatted timestamps
            ),
            yaxis=dict(
                backgroundcolor="rgb(255, 182, 170)",
                title="POI Name",
                tickvals=np.arange(len(y_vals)),
                ticktext=y_vals  # Use POI names
            ),
            zaxis=dict(
                backgroundcolor="rgb(40, 44, 52)",
                title="Dwell Time")
        ),
        width=800,
        margin=dict(r=10, l=10, b=10, t=10)
    )

    return fig1, fig2

if __name__ == "__main__":
    try:
        print("Running Dash app5. Press Ctrl+C to exit.")
        app5.run_server(debug=True)
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt detected. Exiting...")
        