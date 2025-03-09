import streamlit as st
import pandas as pd
import datetime
import ast
import re

# Set the page layout to wide
st.set_page_config(layout="wide")

# Inject CSS to minimize outer and top space
st.markdown("""
    <style>
        /* Reduce padding in the main container */
        .main .block-container {
            padding-top: 0rem;
            padding-right: 1rem;
            padding-left: 1rem;
            padding-bottom: 0rem;
        }
        /* Remove extra top margin from header elements */
        h1 { 
            margin-top: 0.5rem; 
            font-size: 10px;
            padding: 1px;
        }
        h2, h3, h4, h5, h6 { margin-top: 0.2rem; }
    </style>
    """, unsafe_allow_html=True)

# ---- File Paths (Replace with Actual Paths) ----
path = 'D:/Learn/projects/data/job_data/mine/'
raw_data_path = f"{path}linkedin_jobs_fin_acc_02152025_03072025.parquet"
ai_processed_path = f"{path}linkedin_fin_acc_AIprocessed_02152025_to_03072025B.csv"
city_coordinates_path = f"{path}coordinates_city.csv"
state_coordinates_path = f"{path}coordinates_state.csv"
companies_info_path = f"{path}companies_info.csv"

@st.cache_data
def load_data():
    raw = pd.read_parquet(raw_data_path)
    ai_processed = pd.read_csv(
        ai_processed_path,
        usecols=["job_id", "location_st", "state", "avg_salary", "skills_clean",
                 "degree", "min_years_of_experience", "job_title_clean",
                 "job_function_list", "industries_list"]
    )
    city_coordinates = pd.read_csv(city_coordinates_path, usecols=["location", "latitude", "longitude"])
    state_coordinates = pd.read_csv(
        state_coordinates_path,
        usecols=["state", "state_latitude", "state_longitude", "cost_index", "population"]
    )
    merged_df = raw.merge(ai_processed, on="job_id", how="left")
    merged_df.drop(merged_df[merged_df['avg_salary'] > 1000000].index, inplace=True)
    merged_df = merged_df.merge(city_coordinates, left_on="location_st", right_on="location", how="left")
    merged_df = merged_df.merge(state_coordinates, on="state", how="left")
    merged_df['posted_date'] = pd.to_datetime(merged_df['posted_date'], errors='coerce')
    companies_info = pd.read_csv(
        companies_info_path, 
        usecols=['company_name','clean_url','Followers','Website','Verified page','Industry',
                 'Company size','Members','Headquarters','Founded','Specialties','Posts',
                 'Where they live','Where they studied','What they do','What they are skilled at','What they studied']
    )
    return merged_df, companies_info

df, company_df = load_data()

# ---- Determine Valid Date Range from Data ----
min_date = df['posted_date'].min().date() if pd.notnull(df['posted_date'].min()) else datetime.date(2020, 1, 1)
max_date = df['posted_date'].max().date() if pd.notnull(df['posted_date'].max()) else datetime.date.today()

# ---- Prepare Options for Basic Dropdowns ----
state_options = sorted(df['state'].dropna().unique().tolist())
workplace_options = sorted(df['workplace'].dropna().unique().tolist())
seniority_options = sorted(df['seniority_level'].dropna().unique().tolist())
employment_options = sorted(df['employment_type'].dropna().unique().tolist())

# ---- Prepare Options for Job Title (sorted by frequency) ----
if 'job_title_clean' in df.columns:
    title_counts = df['job_title_clean'].value_counts()
    job_title_options = title_counts.index.tolist()  # most frequent first
else:
    job_title_options = []

# ---- Prepare Options for Job Function (parse from job_function_list) ----
job_func_set = set()
if 'job_function_list' in df.columns:
    for row_val in df['job_function_list'].dropna():
        try:
            parsed = ast.literal_eval(row_val)
            if isinstance(parsed, list):
                for func in parsed:
                    job_func_set.add(func.strip())
        except:
            continue
job_func_options = sorted(job_func_set)

# ---- Prepare Options for Industries (parse from industries_list) ----
industry_counts_dict = {}
if 'industries_list' in df.columns:
    for row_val in df['industries_list'].dropna():
        try:
            parsed = ast.literal_eval(row_val)
            if isinstance(parsed, list):
                for ind in parsed:
                    ind_str = ind.strip()
                    industry_counts_dict[ind_str] = industry_counts_dict.get(ind_str, 0) + 1
        except:
            continue
# Sort industries by count descending.
industry_sorted_by_count = sorted(industry_counts_dict.items(), key=lambda x: x[1], reverse=True)
industry_options = [item[0] for item in industry_sorted_by_count]

# ---- Salary Range as a Drop-Down with Options ----
salary_ranges = [
    "All",
    "20k - 40k",
    "40k - 60k",
    "60k - 80k",
    "80k - 100k",
    "100k - 120k",
    "120k - 140k",
    "140k - 160k",
    "160k - 180k",
    "180k - 200k",
    "200k+"
]

# Helper function to parse salary range selection.
def parse_salary_range(selection):
    if selection == "All":
        return None, None
    elif selection == "200k+":
        return 200000, None
    else:
        parts = selection.split("-")
        lower_val = int(parts[0].strip().replace("k","")) * 1000
        upper_val = int(parts[1].strip().replace("k","")) * 1000
        return lower_val, upper_val

st.title("Job Data Dashboard")

# ---- First Row of Filters (4 columns) ----
row1 = st.columns(4)
with row1[0]:
    date_range = st.date_input(
        "Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
with row1[1]:
    selected_state = st.selectbox("State", options=["All"] + state_options)
with row1[2]:
    selected_workplace = st.selectbox("Workplace", options=["All"] + workplace_options)
with row1[3]:
    selected_seniority = st.selectbox("Seniority Level", options=["All"] + seniority_options)

# ---- Second Row of Filters (5 columns) ----
row2 = st.columns(5)
with row2[0]:
    selected_employment = st.selectbox("Employment Type", options=["All"] + employment_options)
with row2[1]:
    if job_title_options:
        selected_title = st.selectbox("Job Title", options=["All"] + job_title_options)
    else:
        selected_title = "All"
with row2[2]:
    selected_job_funcs = st.multiselect("Job Function", options=job_func_options)
with row2[3]:
    selected_inds = st.multiselect("Industries", options=industry_options)
with row2[4]:
    selected_salary_range = st.selectbox("Salary Range", options=salary_ranges)

# ---- Apply Filters to the DataFrame ----
filtered_df = df[
    (df['posted_date'] >= pd.to_datetime(date_range[0])) & 
    (df['posted_date'] <= pd.to_datetime(date_range[1]))
]
if selected_state != "All":
    filtered_df = filtered_df[filtered_df['state'] == selected_state]
if selected_workplace != "All":
    filtered_df = filtered_df[filtered_df['workplace'] == selected_workplace]
if selected_seniority != "All":
    filtered_df = filtered_df[filtered_df['seniority_level'] == selected_seniority]
if selected_employment != "All":
    filtered_df = filtered_df[filtered_df['employment_type'] == selected_employment]
if selected_title != "All":
    filtered_df = filtered_df[filtered_df['job_title_clean'] == selected_title]

# Filter by job_function_list
if selected_job_funcs:
    def row_has_any_funcs(row_val):
        try:
            parsed = ast.literal_eval(row_val)
            if isinstance(parsed, list):
                return any(func.strip() in selected_job_funcs for func in parsed)
        except:
            return False
        return False
    filtered_df = filtered_df[filtered_df['job_function_list'].notnull() & 
                              filtered_df['job_function_list'].apply(row_has_any_funcs)]
    
# Filter by industries_list
if selected_inds:
    def row_has_any_inds(row_val):
        try:
            parsed = ast.literal_eval(row_val)
            if isinstance(parsed, list):
                return any(ind.strip() in selected_inds for ind in parsed)
        except:
            return False
        return False
    filtered_df = filtered_df[filtered_df['industries_list'].notnull() &
                              filtered_df['industries_list'].apply(row_has_any_inds)]

# Apply salary filter
min_sal, max_sal = parse_salary_range(selected_salary_range)
if min_sal is not None and max_sal is not None:
    filtered_df = filtered_df[(filtered_df['avg_salary'] >= min_sal) & (filtered_df['avg_salary'] < max_sal)]
elif min_sal is not None and max_sal is None:
    filtered_df = filtered_df[filtered_df['avg_salary'] >= min_sal]

# ---- Sidebar Navigation ----
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", 
    ["Overview", "Job Map", "Requirements", "Company Info", "Jobs Lookup"]
)

# ---- Route to the Individual Pages ----
if page == "Overview":
    import overview
    overview.main(filtered_df)
elif page == "Job Map":
    import job_map
    job_map.main(filtered_df)
elif page == "Requirements":
    import requirements as requirements
    requirements.main(filtered_df)
elif page == "Company Info":
    import company_info
    company_info.main(filtered_df, company_df)
elif page == "Jobs Lookup":
    import jobs_lookup
    jobs_lookup.main(filtered_df, company_df)
