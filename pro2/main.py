import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Title
st.title("Streamlit Element Demo")

# DataFrame Section
st.subheader("DataFrame")
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie', 'Sumit'],
    'Age': [25, 32, 37, 45],
    'Occupation': ['Engineer', 'Doctor', 'Artist', 'Chef']
})
st.dataframe(df)

# Data Editor Section (Editable DataFrame)
st.subheader("Data Editor")
editable_df = st.data_editor(df)

# Static Table Section
st.subheader("Static Table")
st.table(df)

# Chart Section
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['A', 'B', 'C']
)

# Area chart Section 
st.subheader("Area Chart")
st.area_chart(chart_data)

# Bar Chart Section
st.subheader("Bar Chart")
st.bar_chart(chart_data)

# Line Chart Section 
st.subheader("Line Chart")
st.line_chart(chart_data)

# Scatter Chart Section
st.subheader("Scatter Chart")
scatter_data = pd.DataFrame({
    'x': np.random.rand(100),
    'y': np.random.rand(100),
})
st.scatter_chart(scatter_data)

# Map Section (displaying random points on a map)
st.subheader("Map")
map_data = pd.DataFrame(
    np.random.randn(100, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon']
)
st.map(map_data)

# Python Section (Custom Pyplot Chart)
st.subheader("Python Chart")
fig, ax = plt.subplots()
ax.plot(chart_data['A'], label='A')
ax.plot(chart_data['B'], label='B')
ax.plot(chart_data['C'], label='C')
ax.set_title("Pyplot Line Chart")
ax.legend()
st.pyplot(fig)


#From to hold the interactive elements
with st.form(key="sample_form"):
    
    # Text Input
    st.subheader("Text Inputs")
    name = st.text_input("Enter your name")
    feedback = st.text_area("Provide your feedback")

    # Date and Time
    st.subheader("Date and Time Inputs")
    dob = st.date_input("Select your date of birth")
    time = st.time_input("Choose a preferred time")

    # Selectors
    st.subheader("Selectors")
    choice = st.radio("Choose an option", ['Option 1', 'Option 2', 'Option 3'])
    gender = st.selectbox("Select your gender", ['Male', 'Female', 'Other'])
    slider_value = st.slider("Select a range", 1, 5, step=1)

    # Toggle and Checkbox
    st.subheader("Toggle & Checkboxes")
    notifications = st.checkbox("Enable dark mode?", value=False)

    # Submit Button
    submit_button = st.form_submit_button(label="Submit")

# Outside the form
st.subheader("Buttons")
if st.button("Click Me"):
    st.write("Button clicked!")

# Display form result after submission
if submit_button:
    st.success(f"Thank you, {name}! 🎉")
    st.info(f"Your feedback: {feedback}")
    st.write(f"Date of Birth: {dob}")
    st.write(f"Time selected: {time}")
    st.write(f"Option Chosen: {choice}")
    st.write(f"Gender: {gender}")
    st.write(f"Range Selected: {slider_value}")
    st.write(f"Dark Mode Enabled: {notifications}")