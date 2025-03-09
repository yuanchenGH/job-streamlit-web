import streamlit as st
import pandas as pd
import datetime
import ast
import re

# Helper function to parse entries like '1,712 University of Washington'
def parse_entry(entry):
    entry = entry.strip()
    m = re.match(r'([\d,]+)\s+(.+)', entry)
    if m:
        num_str, name = m.groups()
        num = int(num_str.replace(",", ""))
        return name.strip(), num
    return None, 0

# Example risk calculation function.
def calculate_risk(company_name, company_info):
    row = company_info[company_info["company_name"] == company_name]
    if row.empty:
        return "low"
    website = row["website"].iloc[0] if "website" in row.columns else ""
    members = row["Members"].iloc[0] if "Members" in row.columns else 0
    verified = row["Verified page"].iloc[0] if "Verified page" in row.columns else False
    posts = row["Posts"].iloc[0] if "Posts" in row.columns else 0
    no_website = pd.isna(website) or website.strip() == ""
    not_verified = (not verified) or (str(verified).lower() == "no")
    if no_website and members < 10 and not_verified and posts < 2:
        return "potential scam"
    if (not no_website) and (members < 10) and not_verified and (not website.lower().endswith((".com", ".gov"))):
        return "high"
    return "low"

# Helper to make URL clickable.
def make_clickable(val, link_text):
    return f'<a href="{val}" target="_blank">{link_text}</a>'

# Helper for risk cell color coding.
def risk_color(val):
    if isinstance(val, str):
        v = val.lower()
        if v == "potential scam":
            return "background-color: red; color: white;"
        elif v == "high":
            return "background-color: orange; color: white;"
        else:
            return "background-color: green; color: white;"
    return ""

def main(df, company_info):
    st.header("Jobs Lookup")
    
    # Limit the data to at most 100 jobs to speed up processing.
    df_sample = df.head(100).copy()
    
    # Calculate Risk for each job on the sample.
    df_sample["Risk"] = df_sample["company_name"].apply(lambda x: calculate_risk(x, company_info))
    
    # Convert job_url and company_url to clickable links.
    df_sample["job_url"] = df_sample["job_url"].apply(lambda x: make_clickable(x, "Job url") if pd.notna(x) else "")
    df_sample["company_url"] = df_sample["company_url"].apply(lambda x: make_clickable(x, "Company url") if pd.notna(x) else "")
    
    # Select the desired columns.
    cols_to_display = ["job_title", "job_url", "job_location", "company_name", "company_url",
                       "posted_date", "workplace", "salary", "seniority_level", 
                       "employment_type", "job_function", "industries", "Risk"]
    df_display = df_sample[cols_to_display].copy()
    
    # Format posted_date as string.
    df_display["posted_date"] = df_display["posted_date"].astype(str)
    
    # Define table styles for a more appealing look.
    table_styles = [
        {'selector': 'th',
         'props': [('background-color', '#0074D9'),
                   ('color', 'white'),
                   ('font-size', '16px'),
                   ('padding', '8px'),
                   ('text-align', 'left')]},
        {'selector': 'td',
         'props': [('padding', '8px'),
                   ('font-size', '14px')]},
        {'selector': 'tr:nth-child(even)',
         'props': [('background-color', '#f2f2f2')]}
    ]
    
    # Apply risk color coding to the Risk column, add table styles, and hide the index.
    styled_table = (df_display.style
                    .applymap(risk_color, subset=["Risk"])
                    .set_table_styles(table_styles)
                    .hide(axis="index")
                    .to_html(escape=False))
    
    # Wrap the table in a fixed-height div with vertical scrolling.
    st.markdown(f'<div style="height:600px; overflow-y: auto;">{styled_table}</div>', unsafe_allow_html=True)

# Example usage:
# df = pd.read_csv("jobs.csv")
# company_info = pd.read_csv("companies_info.csv")
# main(df, company_info)
