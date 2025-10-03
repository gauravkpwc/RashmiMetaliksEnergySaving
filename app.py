import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(page_title="Load Profile Chart", layout="wide")

# Title
st.markdown("<h1 style='text-align: center;'>🔧 Load Profile Chart - Rashmi Metaliks</h1>", unsafe_allow_html=True)

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filters")
    selected_date = st.date_input("Select Date", datetime.today())
    start_hour = st.slider("Start Hour", 0, 23, 0)
    end_hour = st.slider("End Hour", 0, 23, 23)
    departments = ['Sintering', 'Pelletizing', 'DRI', 'BF']
    selected_departments = st.multiselect("Select Departments", departments, default=departments)

# Generate time index with 15-minute granularity
start_time = datetime.combine(selected_date, datetime.min.time()) + timedelta(hours=start_hour)
end_time = datetime.combine(selected_date, datetime.min.time()) + timedelta(hours=end_hour)
time_index = pd.date_range(start=start_time, end=end_time, freq='15T')

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

# Identify top 3 peaks and bottom 3 valleys for total load
peak_indices_total = df_filtered['Total Load'].nlargest(3).index
valley_indices_total = df_filtered['Total Load'].nsmallest(3).index

# Calculate Power Factor (simulated)
real_power = df_filtered['Total Load'].mean()
apparent_power = real_power + np.random.normal(loc=20, scale=5)
power_factor = round(real_power / apparent_power, 2)


# Display Power Factor card above chart with bold text and light orange background
st.markdown(
    f"""
    <div style='text-align:right; font-size:20px; margin-bottom:20px;
                background-color:#FFE5CC; padding:10px; border-radius:8px;'>
        ⚡ <b>Power Factor:</b> <b>{power_factor}</b>
    </div>
    """,
    unsafe_allow_html=True
)


# PwC-style orange color palette
orange_palette = {
    'Total Load': '#FD5108',       # Dark orange
    'Sintering': '#5C6975',
    'Pelletizing': '#FF7216',
    'DRI': '#0308DB',
    'BF': '#D2990C'
}

# Plotting
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(df_filtered.index, df_filtered['Total Load'], label='Total Load',
        color=orange_palette['Total Load'], linewidth=2)

# Fill idle load baseline
ax.fill_between(df_filtered.index, 0, idle_baseline, color='gray', alpha=0.3, label='Idle Load Baseline')

# Highlight top 3 peaks and bottom 3 valleys for total load (no legend)
marker_size_total = int(60 * 0.6)
ax.scatter(peak_indices_total, df_filtered.loc[peak_indices_total, 'Total Load'],
           color='red', zorder=5, s=marker_size_total)
ax.scatter(valley_indices_total, df_filtered.loc[valley_indices_total, 'Total Load'],
           color='red', zorder=5, s=marker_size_total)

# Add individual process lines and highlight their peaks/valleys
marker_size_process = int(40 * 0.6)
for dept in selected_departments:
    ax.plot(df_filtered.index, df_filtered[dept], label=dept,
            linestyle='--', alpha=0.9, linewidth=2, color=orange_palette.get(dept, '#FFA07A'))
    peak_indices = df_filtered[dept].nlargest(3).index
    valley_indices = df_filtered[dept].nsmallest(3).index
    ax.scatter(peak_indices, df_filtered.loc[peak_indices, dept], color='red', zorder=5, s=marker_size_process)
    ax.scatter(valley_indices, df_filtered.loc[valley_indices, dept], color='red', zorder=5, s=marker_size_process)

# Formatting
ax.set_title(f'Load Profile on {selected_date.strftime("%d %b")} ({start_hour}:00 to {end_hour}:00)', fontsize=16)
ax.set_xlabel('Time of Day')
ax.set_ylabel('Power Consumption (kW)')
ax.grid(True, linestyle='--', alpha=0.5)
ax.set_xticks(df_filtered.index[::4])
ax.set_xticklabels([ts.strftime('%d %b (%H:%M)') for ts in df_filtered.index[::4]], rotation=45)

# Keep legend inside chart area
ax.legend(loc='upper left')

# Display the chart
st.pyplot(fig)
