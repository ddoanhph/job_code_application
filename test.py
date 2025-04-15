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

# Save data to CSV
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Initial data load
df = load_data()

# Initialize session state
def initialize_session_state():
    defaults = {
        "step": "validate_code",
        "job_code": "",
        "job_title": "",
        "siglum": "AAI",
        "validated_job_code": "",
        "stored_job_title": ""
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
        st.session_state["validated_job_code"] = job_code

def validate_job_title():
    job_code = st.session_state.get("validated_job_code", "")
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
    st.session_state["stored_job_title"] = job_title

def add_to_database(job_code, job_title, siglum):
    global df
    new_row = {'Job_Code': job_code, 'Job_Title': job_title, 'Siglum': siglum}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    save_data(df)  # Save to CSV instead of Dataset

    st.success(f"🚀 Added Job Code '{job_code}' with Title '{job_title}' to database!")
    st.balloons()
    st.dataframe(df.tail())
    reset_form()

def remove_selected_job_codes():
    global df
    # Get the rows that are selected
    selected_df = edited_df[edited_df['select']]
    if not selected_df.empty:
        codes_to_remove = selected_df['Job_Code'].tolist()
        df = df[~df['Job_Code'].isin(codes_to_remove)].reset_index(drop=True)
        save_data(df)
        st.success(f"🗑️ Successfully removed the selected job codes: {', '.join(codes_to_remove)}")
    else:
        st.warning("⚠️ Please select at least one row to remove.")

    # Remove the 'select' column after processing
    if 'select' in df.columns:
        df.drop(columns=['select'], inplace=True)
        # Force a re-run to update the displayed dataframe
        st.rerun()

def reset_form():
    for key in ["job_code", "job_title", "validated_job_code", "stored_job_title"]:
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
        st.write(f"Job Code: **{st.session_state.get('validated_job_code', 'N/A')}**")
        st.text_input("Enter Job Title", key="job_title", max_chars=30)
        st.button("Validate Job Title", on_click=validate_job_title)

    elif st.session_state["step"] == "add_to_db":
        job_code = st.session_state.get("validated_job_code", "")
        job_title = st.session_state.get("stored_job_title", "")

        st.write(f"Job Code: **{job_code}**")
        st.write(f"Job Title: **{job_title}**")

        siglum = st.radio("Select siglum:", options=["AAI", "AHI"],
                            horizontal=True, key="siglum")

        col1, col2 = st.columns(2)
        with col1:
            st.button("Add to Database", on_click=add_to_database,
                        args=(job_code, job_title, st.session_state["siglum"]))
        with col2:
            st.button("Reset Form", on_click=reset_form)

with tab2:
    st.subheader("Remove Job Codes")
    # Add a 'select' column with checkboxes to the DataFrame
    df['select'] = False
    edited_df = st.data_editor(df, column_config={"select": st.column_config.CheckboxColumn("Select")}, num_rows="dynamic")

    if st.button("Remove Selected Job Codes"):
        # Get the rows that are selected
        selected_df = edited_df[edited_df['select']]
        if not selected_df.empty:
            codes_to_remove = selected_df['Job_Code'].tolist()
            global df
            df = df[~df['Job_Code'].isin(codes_to_remove)].reset_index(drop=True)
            save_data(df)
            st.success(f"🗑️ Successfully removed the selected job codes: {', '.join(codes_to_remove)}")
        else:
            st.warning("⚠️ Please select at least one row to remove.")

        # Remove the 'select' column after processing
        if 'select' in df.columns:
            df.drop(columns=['select'], inplace=True)
            # Force a re-run to update the displayed dataframe
            st.rerun()

    # Display the current state of the database
    st.subheader("Current Job Code Database")
    st.dataframe(df)
