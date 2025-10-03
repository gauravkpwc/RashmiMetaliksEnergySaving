import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Load Profile Chart", layout="wide")

st.title("🔧 Load Profile Chart - Rashmi Metaliks")

# Generate a datetime index for 24 hours
time_index = [datetime(2023, 1, 1, hour=h) for h in range(24)]

# Simulated power consumption data (in kW) for each process
np.random.seed(42)
sintering = np.random.normal(loc=180, scale=20, size=24)
pelletizing = np.random.normal(loc=150, scale=15, size=24)
dri = np.random.normal(loc=200, scale=25, size=24)
bf = np.random.normal(loc=220, scale=30, size=24)

# Combine into a DataFrame
df = pd.DataFrame({
    'Time': time_index,
    'Sintering': sintering,
    'Pelletizing': pelletizing,
    'DRI': dri,
    'BF': bf
})
df.set_index('Time', inplace=True)

# Calculate total load and idle load baseline
df['Total Load'] = df.sum(axis=1)
idle_baseline = df['Total Load'].min() * 0.95  # Assume idle load is 95% of minimum total load

# Identify peak demand spikes (above 90th percentile)
peak_threshold = np.percentile(df['Total Load'], 90)
df['Peak'] = df['Total Load'] > peak_threshold

# Plotting
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(df.index, df['Total Load'], label='Total Load', color='blue', linewidth=2)

# Fill idle load baseline
ax.fill_between(df.index, 0, idle_baseline, color='gray', alpha=0.3, label='Idle Load Baseline')

# Highlight peak demand spikes
ax.scatter(df.index[df['Peak']], df['Total Load'][df['Peak']], color='red', label='Peak Demand', zorder=5)

# Add individual process lines
ax.plot(df.index, df['Sintering'], label='Sintering', linestyle='--', alpha=0.6)
ax.plot(df.index, df['Pelletizing'], label='Pelletizing', linestyle='--', alpha=0.6)
ax.plot(df.index, df['DRI'], label='DRI', linestyle='--', alpha=0.6)
ax.plot(df.index, df['BF'], label='BF', linestyle='--', alpha=0.6)

# Formatting
ax.set_title('24-Hour Load Profile - Rashmi Metaliks', fontsize=16)
ax.set_xlabel('Time of Day')
ax.set_ylabel('Power Consumption (kW)')
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper left')
fig.autofmt_xdate()

# Display the chart in Streamlit
