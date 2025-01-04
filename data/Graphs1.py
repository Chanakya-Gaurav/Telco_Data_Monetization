import plotly.express as px
import pandas as pd

# Sample real-time traffic data
data = {
    "Timestamp": ["2024-01-01 10:00", "2024-01-01 11:00", "2024-01-01 12:00"],
    "Affluent Achievers": [120, 150, 170],
    "Suburban Comfort": [80, 90, 100],
    "Urban Professionals": [200, 220, 250],
    "Peri-Urban Residents": [50, 60, 70]
}

# Create DataFrame
df = pd.DataFrame(data)
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# Melt data for Plotly
df_melted = df.melt(id_vars=["Timestamp"], var_name="Lifestyle Preference", value_name="Traffic Density")

# Create a stacked bar chart
fig = px.bar(
    df_melted,
    x="Timestamp",
    y="Traffic Density",
    color="Lifestyle Preference",
    title="Real-Time Traffic Density by Lifestyle Preference",
    labels={"Traffic Density": "Traffic Density", "Timestamp": "Time"},
)

fig.update_layout(barmode="stack")
#fig.show()

import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Sample real-time traffic data
timestamps = pd.date_range(start="2024-01-01 10:00", periods=10, freq="H")
lifestyles = ["Affluent Achievers", "Suburban Comfort", "Urban Professionals", "Peri-Urban Residents"]
traffic_data = np.random.randint(50, 300, size=(len(lifestyles), len(timestamps)))

# Create 3D surface plot
fig = go.Figure()

fig.add_trace(go.Surface(
    z=traffic_data,
    x=timestamps,
    y=lifestyles,
    colorscale="Viridis",
))

# Update layout
fig.update_layout(
    title="Real-Time Traffic Density by Lifestyle Preference",
    scene=dict(
        xaxis_title="Time",
        yaxis_title="Lifestyle Preference",
        zaxis_title="Traffic Density"
    )
)

fig.show()

# Create a DataFrame for the 3D scatter plot
df = pd.DataFrame({
    "Timestamp": np.tile(timestamps, len(lifestyles)),
    "Lifestyle Preference": np.repeat(lifestyles, len(timestamps)),
    "Traffic Density": traffic_data.flatten()
})

# Create 3D scatter plot
fig = go.Figure()

fig.add_trace(go.Scatter3d(
    x=df["Timestamp"],
    y=df["Lifestyle Preference"],
    z=df["Traffic Density"],
    mode='markers',
    marker=dict(
        size=5,
        color=df["Traffic Density"],  # Use density for color
        colorscale='Viridis',
        opacity=0.8
    )
))

# Update layout
fig.update_layout(
    title="Real-Time Traffic Density by Lifestyle Preference",
    scene=dict(
        xaxis_title="Time",
        yaxis_title="Lifestyle Preference",
        zaxis_title="Traffic Density"
    )
)

fig.show()
