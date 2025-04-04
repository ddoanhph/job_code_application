# ... (previous imports and styling remain unchanged)

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
        # Explicitly store job_code in session state
        st.session_state["job_code"] = job_code
        st.session_state["step"] = "validate_title"

def validate_job_title():
    # Retrieve job_code from session state explicitly
    job_code = st.session_state["job_code"].strip()
    job_title = st.session_state["job_title"].strip()
    
    if not job_title:
        st.error("❌ Job Title cannot be empty.")
        return
        
    if not job_code:  # Add a check for empty job_code
        st.error("❌ Job Code is missing. Please start over.")
        st.session_state["step"] = "validate_code"
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
    
    save_data(df)
    
    st.success(f"🚀 Added Job Code '{job_code}' with Title '{job_title}' to database!")
    st.balloons()
    st.dataframe(df.tail())
    reset_form()

def reset_form():
    for key in ["job_code", "job_title"]:
        st.session_state[key] = ""
    st.session_state["step"] = "validate_code"

# Main UI
st.title("Job Code & Title Management")

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

# ... (tab2 for Remove Job Code remains unchanged)
