import streamlit as st

# Title
st.title("User Information Form")

# Form data dictionary
form_value = {
    "name": None,
    "age": None,
    "gender": None,
    "dob": None,
    "location": None
}

# Form
with st.form(key="user_info_form"):
    st.subheader("Please fill the details below:")

    form_value["name"] = st.text_input("Enter your name")
    form_value["age"] = st.number_input("Enter your age", min_value=0, max_value=120, step=1)
    form_value["gender"] = st.selectbox("Select your gender", ['Male', 'Female', 'Other'])
    form_value["dob"] = st.date_input("Select your date of birth")
    form_value["location"] = st.text_input("Enter your location")

    submit = st.form_submit_button(label="Submit")

# Show output after submit
if submit:
    st.success("Form Submitted Successfully!")
    st.write("Here is the data you entered:")

    st.json(form_value)  # nicely shows the whole dictionary as JSON
#0,,2,4,5,7,9,11,12 ||| 0,0,2,0,5,4