import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

# Initialize session state
if 'entries' not in st.session_state:
    st.session_state.entries = pd.DataFrame(columns=["Date", "Start Time", "End Time", "Duration (mins)", "Parent Category", "Sub-Category", "Description"])
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'level' not in st.session_state:
    st.session_state.level = 1
if 'badges' not in st.session_state:
    st.session_state.badges = []
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'last_log_date' not in st.session_state:
    st.session_state.last_log_date = None
if 'daily_goal' not in st.session_state:
    st.session_state.daily_goal = 60  # Minutes per day for challenge
if 'daily_progress' not in st.session_state:
    st.session_state.daily_progress = 0

st.title("Gamified Time Audit Worksheet for EHS and Admin Tasks")
st.write("Track your time, earn points, unlock badges, and level up! Complete daily challenges for bonuses.")

# Gamification Sidebar
with st.sidebar:
    st.header("Your Stats")
    st.metric("Points", st.session_state.points)
    st.metric("Level", st.session_state.level)
    st.progress(st.session_state.points % 100 / 100.0, text=f"Progress to Level {st.session_state.level + 1}")
    st.metric("Streak", f"{st.session_state.streak} days")
    if st.session_state.badges:
        st.subheader("Badges")
        for badge in st.session_state.badges:
            st.write(f"🏆 {badge}")
    st.subheader("Daily Challenge")
    st.progress(st.session_state.daily_progress / st.session_state.daily_goal, text=f"{st.session_state.daily_progress}/{st.session_state.daily_goal} min logged today")

# Input section
date_input = st.date_input("Date", value=date.today())
start_time = st.time_input("Start Time")
end_time = st.time_input("End Time")

parent_category = st.selectbox("Parent Category", ["EHS", "HR", "QA", "ESG", "Other"])

sub_options = ["SDS management", "OSHA log management", "Meeting minutes", "Training records", "Data entry", "Report writing", "Training coordination", "Invoice management", "Other"]
sub_category = st.selectbox("Sub-Category", sub_options)
if sub_category == "Other":
    sub_category = st.text_input("Custom Sub-Category")

description = st.text_input("Task Description")

if st.button("Add Entry & Earn Points"):
    if start_time and end_time and description and sub_category:
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
                    "Parent Category": [parent_category],
                    "Sub-Category": [sub_category],
                    "Description": [description]
                })
                st.session_state.entries = pd.concat([st.session_state.entries, new_entry], ignore_index=True)
                
                # Gamification Logic
                points_earned = int(duration)  # 1 point per minute
                if parent_category in ["EHS", "QA"]:  # Bonus for key parents
                    points_earned += 10
                st.session_state.points += points_earned
                st.success(f"Entry added! +{points_earned} points earned.")
                
                # Update daily progress (only for today's logs)
                if date_input == date.today():
                    st.session_state.daily_progress += int(duration)
                    if st.session_state.daily_progress >= st.session_state.daily_goal and "Daily Challenge" not in st.session_state.badges:
                        st.session_state.points += 50  # Bonus
                        st.session_state.badges.append("Daily Challenge")
                        st.balloons()  # Fun animation
                
                # Streaks
                if st.session_state.last_log_date:
                    if date_input == st.session_state.last_log_date + pd.Timedelta(days=1):
                        st.session_state.streak += 1
                    elif date_input > st.session_state.last_log_date + pd.Timedelta(days=1):
                        st.session_state.streak = 1
                else:
                    st.session_state.streak = 1
                st.session_state.last_log_date = date_input
                
                # Badges
                if len(st.session_state.entries) == 1 and "First Log" not in st.session_state.badges:
                    st.session_state.badges.append("First Log")
                if len(st.session_state.entries) >= 10 and "10 Entries" not in st.session_state.badges:
                    st.session_state.badges.append("10 Entries")
                if st.session_state.streak >= 3 and "3-Day Streak" not in st.session_state.badges:
                    st.session_state.badges.append("3-Day Streak")
                
                # Level Up
                if st.session_state.points // 100 >= st.session_state.level:
                    st.session_state.level += 1
                    st.balloons()  # Celebration
                
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

# Clear button (resets gamification too for demo)
if st.button("Clear All Entries & Reset Game"):
    st.session_state.entries = pd.DataFrame(columns=["Date", "Start Time", "End Time", "Duration (mins)", "Parent Category", "Sub-Category", "Description"])
    st.session_state.points = 0
    st.session_state.level = 1
    st.session_state.badges = []
    st.session_state.streak = 0
    st.session_state.last_log_date = None
    st.session_state.daily_progress = 0
    st.success("Reset complete! Start fresh.")