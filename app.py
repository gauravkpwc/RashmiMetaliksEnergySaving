import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(page_title="Load Profile Dashboard", layout="wide")

# Title
st.markdown("<h1 style='text-align: center;'>🔧 Load Profile Dashboard - Rashmi Metaliks</h1>", unsafe_allow_html=True)

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
data_length = len(time_index)

# Simulated power consumption data
np.random.seed(42)
sintering = np.random.normal(loc=180, scale=20, size=data_length)
pelletizing = np.random.normal(loc=150, scale=15, size=data_length)
dri = np.random.normal(loc=200, scale=25, size=data_length)
bf = np.random.normal(loc=220, scale=30, size=data_length)

# Combine into DataFrame
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

# Identify peaks and valleys
peak_indices_total = df_filtered['Total Load'].nlargest(3).index
valley_indices_total = df_filtered['Total Load'].nsmallest(3).index

# KPIs
real_power = df_filtered['Total Load'].mean()
apparent_power = real_power + np.random.normal(loc=20, scale=5)
power_factor = round(real_power / apparent_power, 2)
load_std_dev = round(df_filtered['Total Load'].std(), 2)
load_cv = round((load_std_dev / real_power) * 100, 2)

# KPI Cards
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div style='background-color:#FFE5CC; padding:10px; border-radius:8px; text-align:center; font-size:18px;'>⚡ <b>Power Factor:</b><br><b>{power_factor}</b></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div style='background-color:#FFE5CC; padding:10px; border-radius:8px; text-align:center; font-size:18px;'>📊 <b>Load Std Dev (σ):</b><br><b>{load_std_dev} kW</b></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div style='background-color:#FFE5CC; padding:10px; border-radius:8px; text-align:center; font-size:18px;'>📈 <b>Coeff. of Variation:</b><br><b>{load_cv} %</b></div>", unsafe_allow_html=True)

# PwC-style colors
orange_palette = {
    'Total Load': '#FD5108',
    'Sintering': '#5C6975',
    'Pelletizing': '#FF7216',
    'DRI': '#0308DB',
    'BF': '#D2990C'
}

# Main Chart
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(df_filtered.index, df_filtered['Total Load'], label='Total Load', color=orange_palette['Total Load'], linewidth=2)
ax.fill_between(df_filtered.index, 0, idle_baseline, color='gray', alpha=0.3, label='Idle Load Baseline')
marker_size_total = int(60 * 0.6)
ax.scatter(peak_indices_total, df_filtered.loc[peak_indices_total, 'Total Load'], color='red', zorder=5, s=marker_size_total)
ax.scatter(valley_indices_total, df_filtered.loc[valley_indices_total, 'Total Load'], color='red', zorder=5, s=marker_size_total)

marker_size_process = int(40 * 0.6)
for dept in selected_departments:
    ax.plot(df_filtered.index, df_filtered[dept], label=dept, linestyle='--', alpha=0.9, linewidth=2, color=orange_palette.get(dept, '#FFA07A'))
    peak_indices = df_filtered[dept].nlargest(3).index
    valley_indices = df_filtered[dept].nsmallest(3).index
    ax.scatter(peak_indices, df_filtered.loc[peak_indices, dept], color='red', zorder=5, s=marker_size_process)
    ax.scatter(valley_indices, df_filtered.loc[valley_indices, dept], color='red', zorder=5, s=marker_size_process)

ax.set_title(f'Load Profile on {selected_date.strftime("%d %b")} ({start_hour}:00 to {end_hour}:00)', fontsize=16)
ax.set_xlabel('Time of Day')
ax.set_ylabel('Power Consumption (kW)')
ax.grid(True, linestyle='--', alpha=0.5)
ax.set_xticks(df_filtered.index[::4])
ax.set_xticklabels([ts.strftime('%d %b (%H:%M)') for ts in df_filtered.index[::4]], rotation=45)
ax.legend(loc='upper left')
st.pyplot(fig)

# Equipment-wise chart
equipment_map = {
    'Sintering': ['Conveyor', 'Blower', 'Heater', 'Compressor', 'Pump', 'Burner'],
    'Pelletizing': ['Conveyor', 'Blower', 'Dryer', 'Compressor', 'Pump', 'Mixer'],
    'DRI': ['Conveyor', 'Blower', 'Reactor', 'Compressor', 'Pump', 'Cooler'],
    'BF': ['Conveyor', 'Blower', 'Stove', 'Compressor', 'Pump', 'Crane']
}

selected_unit = None
if len(selected_departments) == 1:
    selected_unit = selected_departments[0]
elif len(selected_departments) > 1:
    selected_unit = st.selectbox("Select Unit for Equipment View", selected_departments)

if selected_unit:
    equipment_list = equipment_map.get(selected_unit, [])
    selected_equipment = st.selectbox("Select Equipment", ["All"] + equipment_list)

    st.markdown(f"<h3 style='text-align: center;'>🔍 Equipment-wise Load Profile - {selected_unit}</h3>", unsafe_allow_html=True)

    # Simulate equipment data dynamically
    np.random.seed(42)
    equipment_data = {eq: np.random.normal(loc=40, scale=10, size=data_length) for eq in equipment_list}
    df_eq = pd.DataFrame(equipment_data, index=time_index)

    eq_col1, eq_col2 = st.columns([3, 1])
    with eq_col1:
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        if selected_equipment == "All":
            for eq in equipment_list:
                ax2.plot(df_eq.index, df_eq[eq], label=eq, linestyle='--', linewidth=2)
        else:
            ax2.plot(df_eq.index, df_eq[selected_equipment], label=selected_equipment, linestyle='--', linewidth=2)
        ax2.set_title(f'{selected_unit} Equipment Load Profile on {selected_date.strftime("%d %b")}', fontsize=14)
        ax2.set_xlabel('Time of Day')
        ax2.set_ylabel('Power Consumption (kW)')
        ax2.grid(True, linestyle='--', alpha=0.5)
        ax2.set_xticks(df_eq.index[::4])
        ax2.set_xticklabels([ts.strftime("%d %b (%H:%M)") for ts in df_eq.index[::4]], rotation=45)
        ax2.legend(loc='upper left')
        st.pyplot(fig2)

    with eq_col2:
        if selected_equipment == "All":
            total_load = df_eq.sum(axis=1).mean()
        else:
            total_load = df_eq[selected_equipment].mean()
        load_percent = np.random.uniform(60, 80)
        unload_percent = 100 - load_percent
        fig3, ax3 = plt.subplots()
        ax3.pie([load_percent, unload_percent], labels=['Load', 'Unload'], autopct='%1.1f%%',
                colors=['#FD5108', '#FFE5CC'], startangle=90)
        ax3.set_title("Load vs Unload Consumption")
        st.pyplot(fig3)
