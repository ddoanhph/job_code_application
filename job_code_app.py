import streamlit as st
import pandas as pd
import os

PRIMARY_COLOR = "#00205B"
SECONDARY_COLOR = "#A5A5A5"
SUCCESS_COLOR = "#0073E6"
WARNING_COLOR = "#FF6A00"
BACKGROUND_COLOR = "#FFFFFF"

st.markdown(f"""
    <style>
    .stApp {{background-color: {BACKGROUND_COLOR};}}    
    h1, h2, h3, h4, h5, h6 {{color: {PRIMARY_COLOR};}}
    .stButton>button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border-radius: 8px;
    }}
    .stButton>button:hover {{background-color: {SUCCESS_COLOR}; color: white;}}
    .st-alert-success {{color: {SUCCESS_COLOR};}}
    .st-alert-warning {{color: {WARNING_COLOR};}}
    input[type="text"] {{
        background-color: #FFFFFF;
        border: 1px solid {SECONDARY_COLOR};
        padding: 8px;
        border-radius: 4px;
    }}
    .sidebar.sidebar-content {{background-color: {BACKGROUND_COLOR};}}
    </style>
""", unsafe_allow_html=True)

st.markdown(
    f"""
    <style>
    .footer-left {{
        position: fixed;
        left: 10px;
        bottom: 10px;
        font-size: 18px;
        color: #0055A4; 
        font-family: Arial, sans-serif;
    }}
    .footer-right {{
        position: fixed;
        right: 10px;
        bottom: 10px;
        font-size: 18px;
        color: #0055A4;  
        font-family: Arial, sans-serif;
    }}
    </style>
    <div class="footer-left">North America HR Digital Team</div>
    <div class="footer-right">Airbus U.S. Compensation Team</div>
    """,
    unsafe_allow_html=True
)
# Define CSV file path
DATA_FILE = "Combined_Job_Code.csv"

# Load or initialize dataset
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=['Job_Code', 'Job_Title', 'Siglum'])

# Initial data load
df = load_data()

# Initialize session state
def initialize_session_state():
    defaults = {
        "step": "validate_code",
        "job_code": "",
        "job_title": "",
        "siglum": "AAI"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

def validate_job_code():
    job_code = st.session_state["job_code"].strip()
    if len(job_code) < 3:
        st.error("❌ Minimum job code length is 3 characters.")
    elif job_code in df['Job_Code'].values:
        existing_title = df[df['Job_Code'] == job_code]['Job_Title'].values[0]
        st.warning(f"⚠️ Job Code '{job_code}' already exists with title: '{existing_title}'")
        st.dataframe(df[df['Job_Code'] == job_code])
    else:
        st.success(f"✅ Job Code '{job_code}' is unique. Please enter the job title.")
        st.session_state["step"] = "validate_title"

def validate_job_title():
    job_code = st.session_state["job_code"]
    job_title = st.session_state["job_title"].strip()
    
    if not job_title:
        st.error("❌ Job Title cannot be empty.")
        return
        
    existing_titles = df['Job_Title'].str.strip().str.lower()
    if job_title.lower() in existing_titles.values:
        existing_codes = df[existing_titles == job_title.lower()]['Job_Code'].tolist()
        st.warning(f"⚠️ Job Title '{job_title}' already exists with code(s): {existing_codes}")
        st.dataframe(df[df['Job_Code'].isin(existing_codes)])
    else:
        st.success(f"🎉 Job Code '{job_code}' and Job Title '{job_title}' are unique!")
        st.session_state["step"] = "add_to_db"

def add_to_database(job_code, job_title, siglum):
    global df
    new_row = {'Job_Code': job_code, 'Job_Title': job_title, 'Siglum': siglum}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    st.success(f"🚀 Added Job Code '{job_code}' with Title '{job_title}' to database!")
    st.balloons()
    st.dataframe(df.tail())
    reset_form()

def remove_job_code(job_code):
    global df
    if job_code in df['Job_Code'].values:
        df = df[df['Job_Code'] != job_code].reset_index(drop=True)
        save_data(df)  # Save to CSV instead of Dataset
        st.success(f"🗑️ Removed Job Code '{job_code}' from database!")
        st.dataframe(df.tail())
    else:
        st.error(f"❌ Job Code '{job_code}' not found in database.")

def reset_form():
    for key in ["job_code", "job_title"]:
        st.session_state[key] = ""
    st.session_state["step"] = "validate_code"

# Main UI
st.title("Job Code & Title Management")

# Tabs for Add and Remove functionality
tab1, tab2 = st.tabs(["Add Job Code", "Remove Job Code"])

with tab1:
    if st.session_state["step"] == "validate_code":
        job_code_input = st.text_input("Enter Job Code", key="job_code", 
                                     max_chars=6, 
                                     placeholder="E.g., AAA123",
                                     help="Start typing to see matching job codes")
        if st.session_state["job_code"]:
            matching_codes = df[df['Job_Code'].str.startswith(st.session_state["job_code"], na=False)]['Job_Code'].tolist()
            st.write("Matching Job Codes:", matching_codes)
        st.button("Validate Job Code", on_click=validate_job_code)

    elif st.session_state["step"] == "validate_title":
        st.write(f"Job Code: **{st.session_state['job_code']}**")
        st.text_input("Enter Job Title", key="job_title", max_chars=30)
        st.button("Validate Job Title", on_click=validate_job_title)

    elif st.session_state["step"] == "add_to_db":
        job_code = st.session_state["job_code"]
        job_title = st.session_state["job_title"]
        
        st.write(f"Job Code: **{job_code}**")
        st.write(f"Job Title: **{job_title}**")
        
        siglum = st.radio("Select siglum:", options=["AAI", "AHI"], 
                         horizontal=True, key="siglum")
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("Add to Database", on_click=add_to_database, 
                     args=(job_code, job_title, siglum))
        with col2:
            st.button("Reset Form", on_click=reset_form)

with tab2:
    remove_code = st.text_input("Enter Job Code to Remove", 
                              max_chars=6,
                              placeholder="E.g., AAA123")
    if remove_code:
        matching_codes = df[df['Job_Code'].str.startswith(remove_code, na=False)]['Job_Code'].tolist()
        st.write("Matching Job Codes:", matching_codes)
    
    if st.button("Remove Job Code", key="remove_button"):
        if remove_code:
            remove_job_code(remove_code)
        else:
            st.error("❌ Please enter a Job Code to remove.")
