import streamlit as st
import pandas as pd
import plotly.express as px
from foundry.transforms import Dataset
import os

# Constants
PRIMARY_COLOR = "#00205B"
SECONDARY_COLOR = "#A5A5A5"
SUCCESS_COLOR = "#0073E6"
WARNING_COLOR = "#FF6A00"
BACKGROUND_COLOR = "#FFFFFF"

# CSS Styling
st.markdown(f"""
    <style>
    .stApp {{background-color: {BACKGROUND_COLOR};}}
    h1, h2 {{color: {PRIMARY_COLOR};}}
    .stButton>button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
    }}
    .stButton>button:hover {{background-color: {SUCCESS_COLOR};}}
    </style>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
    <style>
    .footer {position: fixed; bottom: 10px; width: 100%; display: flex; justify-content: space-between; padding: 0 20px;}
    .footer span {color: #0055A4; font-family: Arial, sans-serif; font-size: 18px;}
    </style>
    <div class="footer">
        <span>North America HR Digital Team</span>
        <span>Airbus U.S. Compensation Team</span>
    </div>
""", unsafe_allow_html=True)

# Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv("Combined_Job_Code.csv")
    df['Job_Codes'] = df['Job_Code'].apply(lambda x: x.split('-')[0].strip())
    df['Job_Title'] = df['Job_Code'].apply(lambda x: x.split('-')[1].strip())
    df['Occurences'] = pd.to_numeric(df['Occurences'], errors='coerce').fillna(0).astype(int)
    return df[["Job_Code_Group", "Job_Code", "Job_Codes", "Job_Title", "Occurences", 
              "Proposed_Mapping", "HRBP_Owner", "NEW_PROPOSED_CATEGORY"]]

# Initialize session state
def init_session_state():
    defaults = {
        "step": "validate_code",
        "job_code": "",
        "job_title": "",
        "df": load_data()
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

def validate_job_code():
    job_code = st.session_state["job_code"].strip()
    if len(job_code) < 3:
        st.error("❌ Job code must be at least 3 characters long")
        return
    if job_code in st.session_state.df['Job_Codes'].values:
        existing_title = st.session_state.df[st.session_state.df['Job_Codes'] == job_code]['Job_Title'].values[0]
        st.warning(f"⚠️ Job Code '{job_code}' already exists with title '{existing_title}'")
        st.dataframe(st.session_state.df[st.session_state.df['Job_Codes'] == job_code])
    else:
        st.success(f"✅ Job Code '{job_code}' is available")
        st.session_state.step = "validate_title"

def validate_job_title():
    job_title = st.session_state["job_title"].strip()
    if not job_title:
        st.error("❌ Job title cannot be empty")
        return
    if job_title.lower() in st.session_state.df['Job_Title'].str.lower().values:
        existing_codes = st.session_state.df[st.session_state.df['Job_Title'].str.lower() == job_title.lower()]['Job_Codes'].tolist()
        st.warning(f"⚠️ Job Title '{job_title}' already exists with code(s): {existing_codes}")
        st.dataframe(st.session_state.df[st.session_state.df['Job_Codes'].isin(existing_codes)])
    else:
        st.success(f"✅ Job Title '{job_title}' is available")
        st.session_state.step = "add_to_db"

def add_to_database():
    try:
        new_row = {
            'Job_Code_Group': 'Unmapped',
            'Job_Code': f"{st.session_state.job_code} - {st.session_state.job_title}",
            'Job_Codes': st.session_state.job_code,
            'Job_Title': st.session_state.job_title,
            'Occurences': 0,
            'Proposed_Mapping': '',
            'HRBP_Owner': '',
            'NEW_PROPOSED_CATEGORY': ''
        }
        
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Write to dataset
        job_codes_dataset = Dataset.get("job_codes___us_local_job_catalogue_job_code")
        job_codes_dataset.write_table(st.session_state.df)
        
        st.success(f"✅ Successfully added '{st.session_state.job_code} - {st.session_state.job_title}'")
        st.balloons()
        st.dataframe(st.session_state.df.tail())
        
        csv = st.session_state.df.to_csv(index=False)
        st.download_button("Download CSV", csv, "job_codes_database.csv", "text/csv")
        
        reset_form()
    except Exception as e:
        st.error(f"❌ Error adding to database: {str(e)}")

def reset_form():
    st.session_state.job_code = ""
    st.session_state.job_title = ""
    st.session_state.step = "validate_code"

# Main UI
st.title("Job Code & Title Validation")

if st.session_state.step == "validate_code":
    with st.form("job_code_form"):
        st.text_input("Job Code", key="job_code", max_chars=6, placeholder="E.g., AAA123")
        if st.session_state.job_code:
            matches = st.session_state.df[st.session_state.df['Job_Codes'].str.startswith(st.session_state.job_code, na=False)]['Job_Codes'].tolist()
            if matches:
                st.write("Similar codes:", ", ".join(matches))
        submitted = st.form_submit_button("Validate Job Code")
        if submitted:
            validate_job_code()

elif st.session_state.step == "validate_title":
    with st.form("job_title_form"):
        st.write(f"Job Code: **{st.session_state.job_code}**")
        st.text_input("Job Title", key="job_title", max_chars=30)
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Validate Job Title"):
                validate_job_title()
        with col2:
            if st.form_submit_button("Back"):
                reset_form()

elif st.session_state.step == "add_to_db":
    with st.form("add_form"):
        st.write(f"Job Code: **{st.session_state.job_code}**")
        st.write(f"Job Title: **{st.session_state.job_title}**")
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Confirm Add to Database"):
                add_to_database()
        with col2:
            if st.form_submit_button("Cancel"):
                reset_form()
