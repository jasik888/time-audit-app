import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

# Initialize session state for entries
if 'entries' not in st.session_state:
    st.session_state.entries = pd.DataFrame(columns=["Date", "Start Time", "End Time", "Duration (mins)", "Category", "Description"])

st.title("Time Audit Worksheet for EHS and Admin Tasks")
st.write("Track your time on EHS, admin training, QA, HR, and other tasks. Enter details below and add entries. Export to CSV when done.")

# Input section
date_input = st.date_input("Date", value=date.today())
start_time = st.time_input("Start Time")
end_time = st.time_input("End Time")
category = st.selectbox("Task Category", ["EHS Admin", "Admin Training", "Quality Assurance", "HR Tasks", "Other"])
description = st.text_input("Task Description")

if st.button("Add Entry"):
    if start_time and end_time and description:
        try:
            start_dt = datetime.combine(date_input, start_time)
            end_dt = datetime.combine(date_input, end_time)
            if end_dt <= start_dt:
                st.error("End time must be after start time.")
            else:
                duration = (end_dt - start_dt).total_seconds() / 60
                new_entry = pd.DataFrame({
                    "Date": [date_input.strftime("%Y-%m-%d")],
                    "Start Time": [start_time.strftime("%H:%M")],
                    "End Time": [end_time.strftime("%H:%M")],
                    "Duration (mins)": [f"{duration:.0f}"],
                    "Category": [category],
                    "Description": [description]
                })
                st.session_state.entries = pd.concat([st.session_state.entries, new_entry], ignore_index=True)
                st.success("Entry added!")
        except ValueError:
            st.error("Invalid input. Ensure times are correct.")
    else:
        st.error("All fields are required.")

# Display entries
st.subheader("Your Entries")
st.dataframe(st.session_state.entries)

# Export to CSV
if not st.session_state.entries.empty:
    csv_data = st.session_state.entries.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Export to CSV",
        data=csv_data,
        file_name=f"time_audit_{date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Clear button
if st.button("Clear All Entries"):
    st.session_state.entries = pd.DataFrame(columns=["Date", "Start Time", "End Time", "Duration (mins)", "Category", "Description"])
    st.success("Entries cleared!")