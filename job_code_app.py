import streamlit as st
import pandas as pd
from pathlib import Path
import io

# Set the title and favicon that appear in the Browser's tab
st.set_page_config(
    page_title='Job Code Application',
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_job_code_data():
    DATA_FILENAME = Path(__file__).parent/'data/Combined_Job_Code.csv'
    raw_job_code_df = pd.read_csv(DATA_FILENAME)
    return raw_job_code_df

df = get_job_code_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
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

# Display logo at the top
st.image("logo.jpg")  # Adjust the logo size as needed

# Footer text
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

if "step" not in st.session_state:
    st.session_state["step"] = "validate_code"

if "job_code" not in st.session_state:
    st.session_state["job_code"] = ""

if "job_title" not in st.session_state:
    st.session_state["job_title"] = ""

# Function to handle CSV download
def download_csv(df):
    csv = df.to_csv(index=False)
    return csv

# Function to convert CSV to downloadable link
def create_download_link(csv):
    b64 = base64.b64encode(csv.encode()).decode()  # B64 encode CSV to create a downloadable link
    return f'<a href="data:file/csv;base64,{b64}" download="job_codes.csv">Download CSV</a>'

# -----------------------------------------------------------------------------
# Draw the actual page components
def validate_job_code():
    job_code = st.session_state["job_code"]
    if len(job_code) < 3:
        st.error("❌ Minimum job code length is 3.")
    elif job_code in df['Job_Code'].values:
        existing_title = df[df['Job_Code'] == job_code]['Job_Title'].values[0]
        st.warning(f"⚠️ Job Code '{job_code}' already exists! Existing job title is '{existing_title}'")
        st.write(df[df['Job_Code'] == job_code])
    else:
        st.success(f"✅ Job Code '{job_code}' is unique. Please enter the job title.")
        st.session_state["job_code"] = job_code
        st.session_state["step"] = "validate_title"

def validate_job_title():
    job_code = st.session_state.get("job_code", "")
    job_title = st.session_state["job_title"]

    if job_title.strip().lower() in df['Job_Title'].str.strip().str.lower().values:
        existing_code = df[df['Job_Title'].str.strip().str.lower() == job_title.strip().lower()]['Job_Code'].tolist()
        st.warning(f"⚠️ Job Title '{job_title}' already exists with code(s): {existing_code}.")
        st.write(df[(df['Job_Code'].isin(existing_code)) & (df['Job_Code'] != '')])
    else:
        st.snow()
        st.success(f"🎉 Job Code '{job_code}' and Job Title '{job_title}' are unique!")
    st.session_state["job_code"] = job_code
    st.session_state["job_title"] = job_title
    st.session_state["step"] = "add_to_db"

def add_to_database_with_siglum(job_code, job_title, siglum):
    new_row = {'Job_Code': job_code, 'Job_Title': job_title, 'Siglum': siglum}
    global df
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    # How to add the new job code and job title to the database?
    # combined_job_code = Dataset.get("combined_job_code")
    combined_job_code.write_table(df)

    st.success(f"🚀 Added Job Code '{job_code}', Job Title '{job_title}' to the database!")
    st.balloons()
    st.write(df.tail())

    # Provide the download link for CSV
    csv = download_csv(df)
    st.markdown(create_download_link(csv), unsafe_allow_html=True)

    reset_form()

def reset_form():
    st.session_state["job_code"] = ""
    st.session_state["job_title"] = ""
    st.session_state["step"] = "validate_code"

# -----------------------------------------------------------------------------
if st.session_state["step"] == "validate_code":
    job_code_input = st.text_input("Enter Job Code", key="job_code", max_chars=6, placeholder="E.g., AAA123",
                                   help="Start typing to see matching job codes.")
    matching_codes = df[df['Job_Code'].str.startswith(st.session_state["job_code"], na=False)]['Job_Code'].tolist()

    if st.session_state["job_code"]:
        st.write("Matching Job Codes:")
        st.write(matching_codes)

    st.button("Validate Job Code", on_click=validate_job_code)

elif st.session_state["step"] == "validate_title":
    st.write(f"Job Code: **{st.session_state.get('job_code', '')}**")
    job_title_input = st.text_input("Enter Job Title", key="job_title", max_chars=30)
    st.button("Validate Job Title", on_click=validate_job_title)

elif st.session_state["step"] == "add_to_db":
    # Retrieve job code and title from session state
    job_code = st.session_state.get("job_code", "")
    job_title = st.session_state.get("job_title", "")

    st.write(f"Job Code: **{job_code}**")
    st.write(f"Job Title: **{job_title}**")

    siglum = st.radio(
        "Select the siglum for this job code and title:",
        options=["AAI", "AHI"],
        index=0 if "siglum" not in st.session_state else ["AAI", "AHI"].index(st.session_state["siglum"]),
        horizontal=True,
        key="siglum"
    )

    # Preserve job code and title on siglum update
    st.session_state["job_code"] = job_code
    st.session_state["job_title"] = job_title

    if st.button("Add Job Code & Title to Database"):
        add_to_database_with_siglum(job_code, job_title, siglum)
    st.button("Reset Form", on_click=reset_form)
