import streamlit as st
import pandas as pd
import ast
import os
import bcrypt
from sqlalchemy import create_engine
from dotenv import load_dotenv


# Load user credentials from file
@st.cache_data
def load_user_credentials(filepath="users.csv"):
    users_df = pd.read_csv(filepath)
    user_dict = dict(zip(users_df["username"], users_df["password_hash"]))
    return user_dict

# Authentication function
def authenticate(username, password, user_credentials):
    if username in user_credentials:
        stored_hash = user_credentials[username].encode("utf-8")
        if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            return True
    return False

def read_sql_uppercase(query, engine):
    df = pd.read_sql(query, engine)
    df.columns = [col.upper() for col in df.columns]
    return df

# # Load users
# user_credentials = load_user_credentials("users.csv")

# # Check session state
# if "authenticated" not in st.session_state:
#     st.session_state["authenticated"] = False
#     # st.session_state["authenticated"] = True

# if not st.session_state["authenticated"]:
#     st.title("🔐 Secure Login")

#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")

#     if st.button("Login"):
#         if authenticate(username, password, user_credentials):
#             st.session_state["authenticated"] = True
#             st.success("✅ Login successful!")
#             st.rerun()
#         else:
#             st.error("❌ Invalid username or password")

#     st.stop()

load_dotenv()

snowflake_username = os.getenv('SNOWFLAKE_USERNAME')
snowflake_password = os.getenv('SNOWFLAKE_PASSWORD')
snowflake_account = os.getenv('SNOWFLAKE_ACCOUNT')

# Set the page layout to wide
st.set_page_config(layout="wide")

# Inject CSS to minimize outer and top space
st.markdown("""
    <style>
        .main .block-container {
            padding-top: 0rem;
            padding-right: 1rem;
            padding-left: 1rem;
            padding-bottom: 0rem;
        }
        h1 { 
            margin-top: 0.5rem; 
            font-size: 10px;
            padding: 1px;
        }
        h2, h3, h4, h5, h6 { margin-top: 0.2rem; }
    </style>
    """, unsafe_allow_html=True)

# ---- File Paths ----
path = 'D:/Learn/projects/data/job_data/mine/'

@st.cache_data
def load_data():
    conn_str = (
    f"snowflake://{snowflake_username}:{snowflake_password}@{snowflake_account}/"
    f"LINKEDIN_JOBS/PUBLIC?warehouse=COMPUTE_WH&role=ACCOUNTADMIN"
    )
    engine = create_engine(conn_str)

    query_jobs = """
    SELECT 
        AI.JOB_ID,
        AI.JOB_TITLE,
        R.WORKPLACE,
        R.JOB_URL,
        R.SENIORITY_LEVEL,
        R.EMPLOYMENT_TYPE,
        R.JOB_FUNCTION,
        R.INDUSTRIES,
        R.COMPANY_NAME,
        R.COMPANY_URL,
        R.SALARY,
        TO_DATE(AI.POSTED_DATE, 'MM/DD/YYYY') AS POSTED_DATE,
        AI.AVG_SALARY,
        AI.SKILLS_MATCHED,
        AI.DEGREE,
        AI.MIN_YEARS_OF_EXPERIENCE,
        AI.PRIMARY_TITLE,
        AI.SUB_TITLE,
        AI.JOB_FUNCTION_LIST,
        AI.LOCATION_ST AS LOCATION,
        AI.STATE
    FROM LINKEDIN_FIN_ACC_AI AI
    LEFT JOIN LINKEDIN_FIN_ACC_RAW R 
      ON R.JOB_ID = AI.JOB_ID
    WHERE AI.POSTED_DATE > '02/22/2025'
          AND (AI.AVG_SALARY > 20000 AND AI.AVG_SALARY < 500000
           OR AI.AVG_SALARY IS NULL)
    ORDER BY AI.POSTED_DATE DESC;
    """

    merged_df = read_sql_uppercase(query_jobs, engine)
    merged_df['POSTED_DATE'] = pd.to_datetime(merged_df['POSTED_DATE'], errors='coerce')

    query_companies = """SELECT 
                                CLEAN_URL,
                                COMPANY_NAME,
                                COMPANY_SIZE,
                                FOLLOWERS,
                                FOUNDED,
                                HEADQUARTERS,
                                INDUSTRY,
                                MEMBERS,
                                POSTS,
                                SPECIALTIES,
                                VERIFIED_PAGE,
                                WEBSITE,
                                WHAT_THEY_ARE_SKILLED_AT,
                                WHAT_THEY_DO,
                                WHAT_THEY_STUDIED,
                                WHERE_THEY_LIVE,
                                WHERE_THEY_STUDIED
                         FROM COMPANIES_INFO
                      """
    companies_info = read_sql_uppercase(query_companies, engine)

    query_state_coordinates = "SELECT * FROM COORDINATES_STATE"
    state_df = read_sql_uppercase(query_state_coordinates, engine)

    query_city_coordinates = "SELECT * FROM COORDINATES_CITY"
    city_df = read_sql_uppercase(query_city_coordinates, engine)

    query_job_titles = "SELECT PRIMARY_TITLE FROM job_title_counts ORDER BY count DESC;"
    job_title_options = read_sql_uppercase(query_job_titles, engine)['PRIMARY_TITLE'].tolist()

    query_job_functions = "SELECT job_function FROM job_function_counts ORDER BY count DESC;"
    job_func_options = read_sql_uppercase(query_job_functions, engine)['JOB_FUNCTION'].tolist()

    # conn.close()
    return merged_df, companies_info, state_df, city_df, job_title_options, job_func_options

df, company_df, state_df, city_df, job_title_options, job_func_options = load_data()

# Remove double quotes
job_title_options = [title.replace('"', '') for title in job_title_options]
job_func_options = [func.replace('"', '') for func in job_func_options]

min_date = df['POSTED_DATE'].min()
max_date = df['POSTED_DATE'].max()

state_options = sorted(state_df['STATE'].unique().tolist())
workplace_options = ['onsite', 'hybrid', 'remote']
seniority_options = ['Internship', 'Entry level', 'Associate', 'Mid-Senior level', 'Director', 'Executive', 'Not Applicable']
employment_options = ['Full-time', 'Internship', 'Part-time', 'Contract', 'Temporary', 'Volunteer', 'Other']

salary_ranges = [
    "All", "20K - 40K", "40K - 60K", "60K - 80K", "80K - 100K",
    "100K - 120K", "120K - 140K", "140K - 160K", "160K - 180K",
    "180K - 200K", "200K+"
]

# ✅ Make sure active_page is preserved across reruns
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Overview"

# Sidebar navigation linked to session state
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Overview", "Job Map", "Requirements", "Company Info", "Jobs Lookup", "Other Resources"],
    index=["Overview", "Job Map", "Requirements", "Company Info", "Jobs Lookup", "Other Resources"].index(st.session_state["active_page"]),
    key="active_page"
)

st.title("Job Data Dashboard")

with st.form(key="filters_form"):
    row1 = st.columns(4)
    row2 = st.columns(4)

    with row1[0]:
        date_range = st.date_input(
            "Date Range",
            value=st.session_state.get("date_range", [min_date, max_date]),
            min_value=min_date,
            max_value=max_date,
            key="date_range"
        )
    with row1[1]:
        selected_state = st.selectbox("State", options=["All"] + state_options, key="selected_state")
    with row1[2]:
        selected_workplace = st.selectbox("Workplace", options=["All"] + workplace_options, key="selected_workplace")
    with row1[3]:
        selected_seniority = st.selectbox("Seniority Level", options=["All"] + seniority_options, key="selected_seniority")

    with row2[0]:
        selected_job_title = st.selectbox("Job Title", options=["All"] + job_title_options, key="selected_job_title")
    with row2[1]:
        selected_job_func = st.selectbox("Job Function", options=["All"] + job_func_options, key="selected_job_func")
    with row2[2]:
        selected_salary = st.selectbox("Salary Range", options=salary_ranges, key="selected_salary")

    cols = st.columns(6)
    with cols[0]:
        submit_button = st.form_submit_button(label="Apply Filters")
    with cols[1]:
        reset_button = st.form_submit_button(label="Reset Filters")

if reset_button:
    for key in ["date_range", "selected_state", "selected_workplace", "selected_seniority", "selected_job_title", "selected_job_func", "selected_salary"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1])

filtered_df = df[(df['POSTED_DATE'] >= start_date) & (df['POSTED_DATE'] <= end_date)]

if selected_state != "All":
    filtered_df = filtered_df[filtered_df['STATE'] == selected_state]
if selected_workplace != "All":
    filtered_df = filtered_df[filtered_df['WORKPLACE'] == selected_workplace]
if selected_seniority != "All":
    filtered_df = filtered_df[filtered_df['SENIORITY_LEVEL'] == selected_seniority]
if selected_job_title != "All":
    filtered_df = filtered_df[filtered_df['PRIMARY_TITLE'] == selected_job_title]
if selected_job_func != "All":
    filtered_df = filtered_df[filtered_df['JOB_FUNCTION_LIST'].apply(
        lambda x: selected_job_func in ast.literal_eval(x) if isinstance(x, str) else False
    )]
if selected_salary != "All":
    salary_min, salary_max = selected_salary.replace("K", "").split(" - ")
    salary_min = int(salary_min) * 1000
    salary_max = int(salary_max) * 1000 if salary_max != "+" else float('inf')
    filtered_df = filtered_df[
        (filtered_df['AVG_SALARY'] >= salary_min) & (filtered_df['AVG_SALARY'] <= salary_max)
    ]

# ✅ Route to the selected page (which stays remembered)
if st.session_state["active_page"] == "Overview":
    import overview
    overview.main(filtered_df)
elif st.session_state["active_page"] == "Job Map":
    import job_map
    job_map.main(filtered_df, state_df, city_df)
elif st.session_state["active_page"] == "Requirements":
    import requirements
    requirements.main(filtered_df)
elif st.session_state["active_page"] == "Company Info":
    import company_info
    company_info.main(filtered_df, company_df)
elif st.session_state["active_page"] == "Jobs Lookup":
    import jobs_lookup
    jobs_lookup.main(filtered_df, company_df)
elif st.session_state["active_page"] == "Other Resources":
    import other_res
    other_res.main()