import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(page_title="Load Profile Chart", layout="wide")

st.title("🔧 Load Profile Chart - Rashmi Metaliks")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Date selector
selected_date = st.sidebar.date_input("Select Date", datetime.today())

# Time range selector
start_hour = st.sidebar.slider("Start Hour", 0, 23, 0)
end_hour = st.sidebar.slider("End Hour", 0, 23, 23)

# Department selector
departments = ['Sintering', 'Pelletizing', 'DRI', 'BF']
selected_departments = st.sidebar.multiselect("Select Departments", departments, default=departments)

# Generate time index based on selected date and time range
time_index = [datetime.combine(selected_date, "(" + datetime.min.time()) + timedelta(hours=h) for h in range(start_hour, end_hour + 1) + ")"]

# Simulated power consumption data (in kW) for each process
np.random.seed(42)
data_length = len(time_index)
sintering = np.random.normal(loc=180, scale=20, size=data_length)
pelletizing = np.random.normal(loc=150, scale=15, size=data_length)
dri = np.random.normal(loc=200, scale=25, size=data_length)
bf = np.random.normal(loc=220, scale=30, size=data_length)

# Combine into a DataFrame
df = pd.DataFrame({
    'Time': time_index,
    'Sintering': sintering,
    'Pelletizing': pelletizing,
    'DRI': dri,
    'BF': bf
})
df.set_index('Time', inplace=True)

# Filter selected departments
df_filtered = df[selected_departments]

# Calculate total load and idle load baseline
df_filtered['Total Load'] = df_filtered.sum(axis=1)
idle_baseline = df_filtered['Total Load'].min() * 0.95

# Identify peak demand spikes (above 90th percentile)
peak_threshold = np.percentile(df_filtered['Total Load'], 90)
df_filtered['Peak'] = df_filtered['Total Load'] > peak_threshold

# Calculate Power Factor (simulated)
real_power = df_filtered['Total Load'].mean()
apparent_power = real_power + np.random.normal(loc=20, scale=5)
power_factor = round(real_power / apparent_power, 2)

# Display Power Factor card
st.metric(label="⚡ Power Factor", value=f"{power_factor}")

# Plotting
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(df_filtered.index, df_filtered['Total Load'], label='Total Load', color='blue', linewidth=2)

# Fill idle load baseline
ax.fill_between(df_filtered.index, 0, idle_baseline, color='gray', alpha=0.3, label='Idle Load Baseline')

# Highlight peak demand spikes
ax.scatter(df_filtered.index[df_filtered['Peak']], df_filtered['Total Load'][df_filtered['Peak']], color='red', label='Peak Demand', zorder=5)

# Add individual process lines
for dept in selected_departments:
    ax.plot(df_filtered.index, df_filtered[dept], label=dept, linestyle='--', alpha=0.6)

# Formatting
ax.set_title(f'Load Profile on {selected_date.strftime("%Y-%m-%d")} ({start_hour}:00 to {end_hour}:00)', fontsize=16)
ax.set_xlabel('Time of Day')
ax.set_ylabel('Power Consumption (kW)')
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper left')
fig.autofmt_xdate()

# Display the chart in Streamlit
st.pyplot(fig)
