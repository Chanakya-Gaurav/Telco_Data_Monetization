import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Initialize dataset with a rolling window of 10 timestamps
# Simulate real-time dwell time data for POIs (Points of Interest)
pois = ["POI 1", "POI 2", "POI 3", "POI 4", "POI 5"]  # List of Points of Interest
lifestyles = ["Affluent Achievers", "Suburban Comfort", "Urban Professionals", "Peri-Urban Residents"]

timestamps = [datetime.now() - timedelta(minutes=i) for i in range(10)]
traffic_data = {
    "Timestamp": timestamps[::-1],
    "Affluent Achievers": np.random.randint(50, 300, 10),
    "Suburban Comfort": np.random.randint(50, 300, 10),
    "Urban Professionals": np.random.randint(50, 300, 10),
    "Peri-Urban Residents": np.random.randint(50, 300, 10)
}
lifestyle_df = pd.DataFrame(traffic_data)

# Simulate dwell time (in seconds) at each POI for each timestamp
dwell_time_data = {
    "Timestamp": timestamps[::-1],
    "POI 1": np.random.randint(30, 300, 10),
    "POI 2": np.random.randint(30, 300, 10),
    "POI 3": np.random.randint(30, 300, 10),
    "POI 4": np.random.randint(30, 300, 10),
    "POI 5": np.random.randint(30, 300, 10)
}
dwell_time_df = pd.DataFrame(dwell_time_data)

# Create DataFrame
lifestyle_df["Timestamp"] = pd.to_datetime(lifestyle_df["Timestamp"])

# Simulate real-time data ingestion
def add_new_data(lifestyle_df, dwell_time_df):
    # Generate a new timestamp
    new_timestamp = datetime.now()

    # Generate new data points
    new_data = pd.DataFrame({
        "Timestamp": [new_timestamp],
        "Affluent Achievers": [np.random.randint(50, 300)],
        "Suburban Comfort": [np.random.randint(50, 300)],
        "Urban Professionals": [np.random.randint(50, 300)],
        "Peri-Urban Residents": [np.random.randint(50, 300)]
    })

    # Append to DataFrame and maintain a rolling window of 10
    lifestyle_df = pd.concat([lifestyle_df, new_data], ignore_index=True)
    if len(lifestyle_df) > 10:  # Keep only the last 10 timestamps
        lifestyle_df = lifestyle_df.iloc[1:]

    #Generate new event for dwell time
    new_dwell_time_data = pd.DataFrame({
        "Timestamp": [new_timestamp],
        "POI 1": [np.random.randint(30, 300)],
        "POI 2": [np.random.randint(30, 300)],
        "POI 3": [np.random.randint(30, 300)],
        "POI 4": [np.random.randint(30, 300)],
        "POI 5": [np.random.randint(30, 300)]
    })
    dwell_time_df = pd.concat([dwell_time_df, new_dwell_time_data], ignore_index=True)
    if len(dwell_time_df) > 10:  # Keep only the last 10 timestamps
        dwell_time_df = dwell_time_df.iloc[1:]
    
    print(dwell_time_df)

    return lifestyle_df, dwell_time_df

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Initialize Dash rt_surface
rt_surface = Dash(__name__)

# Layout
rt_surface.layout = html.Div([
    dcc.Graph(id='traffic-density-graph'),
    dcc.Graph(id='3d-surface-graph'),
    dcc.Graph(id='3d-scatter-graph'),  # Added 3D Scatter plot
    dcc.Graph(id='3d-dwell-heatmap'),  # Added 3D Scatter plot
    dcc.Interval(
        id='interval-component',
        interval=2000,  # Update every 2 seconds
        n_intervals=0
    )
])

# Callback to update the graph
@rt_surface.callback(
    Output('traffic-density-graph', 'figure'),
    Output('3d-surface-graph', 'figure'),
    Output('3d-scatter-graph', 'figure'),
    Output('3d-dwell-heatmap', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n_intervals):
    global lifestyle_df
    global dwell_time_df
    # Add new data point
    lifestyle_df, dwell_time_df = add_new_data(lifestyle_df, dwell_time_df)
    
    # Create a line chart (fig1)
    fig1 = go.Figure()
    for lifestyle in ["Affluent Achievers", "Suburban Comfort", "Urban Professionals", "Peri-Urban Residents"]:
        fig1.add_trace(go.Scatter(
            x=lifestyle_df["Timestamp"],
            y=lifestyle_df[lifestyle],
            mode='lines+markers',
            name=lifestyle
        ))
    
    # Update layout for line chart
    fig1.update_layout(
        title="Real-Time Traffic Density by Lifestyle Preference",
        xaxis_title="Time",
        yaxis_title="Traffic Density",
        xaxis=dict(tickformat="%H:%M:%S")  # Show time only
    )

    # 3D Surface Graph (fig2)
    fig2 = go.Figure()

    # Convert timestamps to integers for surface plot
    #x_vals = lifestyle_df["Timestamp"].values.astype(np.int64)  # Convert Timestamp to int for plotting
    x_vals = lifestyle_df["Timestamp"].dt.strftime('%H:%M:%S').values  # Format the Timestamp to hh:mm:ss
    y_vals = ["Affluent Achievers", "Suburban Comfort", "Urban Professionals", "Peri-Urban Residents"]
    
    # Create meshgrid for x and y
    X, Y = np.meshgrid(x_vals, np.arange(len(y_vals)))
    Z = np.array([lifestyle_df[lifestyle].values for lifestyle in y_vals])

    fig2.add_trace(go.Surface(
        z=Z,
        x=X,
        y=Y,
        colorscale="Viridis",
        showscale=True
    ))

    # Update layout for surface graph
    fig2.update_layout(
        title="Real-Time Traffic Density by Lifestyle Preference",
        scene=dict(
            xaxis_title="Time",
            yaxis_title="Lifestyle Preference",
            zaxis_title="Traffic Density",
            xaxis=dict(
                tickmode='array',  # Use custom tick values
                tickvals=x_vals,   # Set the custom ticks based on the formatted time
                ticktext=x_vals    # Set the tick labels to the formatted time
            ),
            yaxis=dict(
                tickmode='array',  # Use custom tick values
                tickvals=np.arange(len(y_vals)),  # Set tick values to indices of lifestyles
                ticktext=y_vals   # Set the tick labels to lifestyle names
            )  # Prevent time distortion in surface
        ),
        autosize=False,
        #scene_camera_eye=dict(x=1.87, y=0.88, z=-0.64),
        width=700, height=500,
        margin=dict(l=65, r=50, b=65, t=90)
    )

    # 3D Scatter Plot (fig3)
    # 3D Scatter Plot (fig3)
    fig3 = go.Figure()

    # Get the global minimum and maximum traffic density values across all lifestyles
    z_min = lifestyle_df[["Affluent Achievers", "Suburban Comfort", "Urban Professionals", "Peri-Urban Residents"]].min().min()
    z_max = lifestyle_df[["Affluent Achievers", "Suburban Comfort", "Urban Professionals", "Peri-Urban Residents"]].max().max()

    # Create 3D scatter plot data
    for i, lifestyle in enumerate(["Affluent Achievers", "Suburban Comfort", "Urban Professionals", "Peri-Urban Residents"]):
        fig3.add_trace(go.Scatter3d(
            x=lifestyle_df["Timestamp"],  # Time values for the x-axis
            y=np.full_like(lifestyle_df["Timestamp"], i),  # Encode lifestyle categories as numeric (0, 1, 2, 3)
            z=lifestyle_df[lifestyle],  # Traffic density for the z-axis
            mode='markers',
            marker=dict(
                size=5, 
                color=lifestyle_df[lifestyle],  # Use density for color
                colorscale='Viridis',
                opacity=0.8,
                cmin=z_min,  # Set the minimum z-value for the color scale
                cmax=z_max   # Set the maximum z-value for the color scale
            ),
            name=lifestyle
        ))

    # Update layout for scatter plot
    fig3.update_layout(
        title="3D Scatter Plot of Traffic Density by Lifestyle Preference",
        scene=dict(
            xaxis_title="Time",
            yaxis_title="Lifestyle Preference",
            zaxis_title="Traffic Density"
        )
    )

    # Set up the Surface Map for Dwell Time by POI
    fig4 = go.Figure()

    # Convert timestamps to string for x-axis (time in hh:mm:ss)
    x_vals = dwell_time_df["Timestamp"].dt.strftime('%H:%M:%S').values  # Formatted time for x-axis
    y_vals = pois  # POIs as y-axis labels

    # Create meshgrid for x and y axes
    X, Y = np.meshgrid(x_vals, np.arange(len(y_vals)))
    Z = np.array([dwell_time_df[poi].values for poi in y_vals])  # Dwell time at each POI over time

    # Add heatmap trace
    fig4.add_trace(go.Surface(
        z=Z,  # Dwell time data (z-axis)
        x=X,  # Time values for x-axis
        y=Y,  # POIs for y-axis
        #colorscale='Viridis',  # Color scale for the heatmap
        showscale=True
    ))

    # Update layout for 3D heatmap
    fig4.update_layout(
        title="Real-Time Dwell Time by POI",
        scene=dict(
            xaxis_title="Time",
            yaxis_title="POI",
            zaxis_title="Dwell Time (Seconds)",
            xaxis=dict(
                tickmode='array',  # Use formatted time on x-axis
                tickvals=x_vals,   # Set custom ticks
                ticktext=x_vals    # Set formatted time labels
            ),
            yaxis=dict(
                tickmode='array',  # Use POI names as y-axis labels
                tickvals=np.arange(len(y_vals)),  # Set numeric values for POIs
                ticktext=y_vals    # Set POI names as labels
            )
        ),
        autosize=False,
        width=1000, height=600,
        margin=dict(l=65, r=50, b=65, t=90)
    )

    return fig1, fig2, fig3, fig4

# Run the rt_surface
if __name__ == '__main__':
    rt_surface.run_server(debug=True)
