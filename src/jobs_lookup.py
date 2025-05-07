import streamlit as st
import pandas as pd
import re
import difflib
import math

# Helper function to parse entries like '1,712 University of Washington'
def parse_entry(entry):
    entry = entry.strip()
    m = re.match(r'([\d,]+)\s+(.+)', entry)
    if m:
        num_str, name = m.groups()
        num = int(num_str.replace(",", ""))
        return name.strip(), num
    return None, 0

# Risk calculation function with explanations
def calculate_risk(company_name, company_info):
    row = company_info[company_info["COMPANY_NAME"] == company_name]
    
    # If company is not in database
    if row.empty:
        return "Not in Database", "Company information is not available in our records."

    website = row["WEBSITE"].iloc[0] if "WEBSITE" in row.columns else ""
    members = row["MEMBERS"].iloc[0] if "MEMBERS" in row.columns else 0
    verified = row["VERIFIED_PAGE"].iloc[0] if "VERIFIED_PAGE" in row.columns else False
    posts = row["POSTS"].iloc[0] if "POSTS" in row.columns else 0
    
    no_website = pd.isna(website) or website.strip() == ""
    not_verified = (not verified) or (str(verified).lower() == "no")

    if no_website and members < 10 and not_verified and posts < 2:
        return "Potential Scam", "Company has no website, few members, is not verified, and has minimal activity."
    if (not no_website) and (members < 10) and not_verified and (not website.lower().endswith((".com", ".gov"))):
        return "High", "Company is not verified, has a small online presence, and an untrusted website."
    
    return "Low", "Company is verified, has an established online presence, and seems legitimate."

# Helper to make URL clickable.
def make_clickable(val, link_text):
    return f'<a href="{val}" target="_blank">{link_text}</a>'

# Helper for risk cell color coding and tooltip.
def risk_color_with_tooltip(risk, reason):
    colors = {
        "Potential Scam": "background-color: red; color: white;",
        "High": "background-color: orange; color: white;",
        "Not in Database": "background-color: gray; color: white;",
        "Low": "background-color: green; color: white;",
    }
    tooltip_html = f'title="{reason}"'  # Tooltip text on hover
    color_style = colors.get(risk, "")
    return f'<td style="{color_style}" {tooltip_html}>{risk}</td>'

def main(df, company_info):
    st.header("Jobs Lookup")
    
    import math

    # Add company search box
    search_query = st.text_input("🔍 Search for a company (partial name accepted):")

    if search_query:
        # Find top 3 closest matches using fuzzy matching
        all_company_names = company_info["COMPANY_NAME"].dropna().unique().tolist()
        top_matches = difflib.get_close_matches(search_query, all_company_names, n=3, cutoff=0.3)
        
        if top_matches:
            st.subheader("Top 3 matching companies:")
            for name in top_matches:
                row = company_info[company_info["COMPANY_NAME"] == name].iloc[0]
                risk, explanation = calculate_risk(name, company_info)
                
                # Safely format founded year (remove .0 if float)
                founded_raw = row['FOUNDED']
                if pd.notna(founded_raw):
                    if isinstance(founded_raw, (float, int)) and not math.isnan(founded_raw):
                        founded = str(int(founded_raw))
                    else:
                        founded = str(founded_raw)
                else:
                    founded = 'N/A'
                
                st.markdown(f"### 🏢 **{name}**")
                st.markdown(f"- 📍 **Headquarters**: {row['HEADQUARTERS'] if pd.notna(row['HEADQUARTERS']) else 'N/A'}")
                st.markdown(f"- 🏭 **Industry**: {row['INDUSTRY'] if pd.notna(row['INDUSTRY']) else 'N/A'}")
                st.markdown(f"- 🌐 **Website**: {row['WEBSITE'] if pd.notna(row['WEBSITE']) else 'N/A'}")
                st.markdown(f"- 📅 **Founded**: {founded}")
                st.markdown(f"- ✅ **Verified**: {row['VERIFIED_PAGE'] if pd.notna(row['VERIFIED_PAGE']) else 'N/A'}")
                st.markdown(f"- 👥 **Members**: {row['MEMBERS'] if pd.notna(row['MEMBERS']) else 'N/A'}")
                st.markdown(f"- ⚠️ **Risk Level**: `{risk}` — {explanation}")
                st.markdown("---")
        else:
            st.warning("No similar companies found.")

    
    st.subheader("Top 100 Jobs Overview")
    
    # Limit the data to at most 100 jobs to speed up processing.
    df_sample = df.head(100).copy()

    if df_sample.empty:
        st.warning("No job data available to display.")
        return  # Exit early
    
    # Calculate Risk for each job and store explanations
    df_sample["Risk"], df_sample["Risk_Explanation"] = zip(*df_sample["COMPANY_NAME"].apply(lambda x: calculate_risk(x, company_info)))
    
    # Convert job_url and company_url to clickable links.
    df_sample["JOB_URL"] = df_sample["JOB_URL"].apply(lambda x: make_clickable(x, "JOB_URL") if pd.notna(x) else "")
    df_sample["COMPANY_URL"] = df_sample["COMPANY_URL"].apply(lambda x: make_clickable(x, "Company url") if pd.notna(x) else "")
    
    # Select the desired columns.
    cols_to_display = ["JOB_TITLE", "JOB_URL", "LOCATION", "COMPANY_NAME", "COMPANY_URL",
                       "POSTED_DATE", "WORKPLACE", "AVG_SALARY", "SENIORITY_LEVEL", 
                       "EMPLOYMENT_TYPE", "JOB_FUNCTION", "INDUSTRIES", "Risk", "Risk_Explanation"]
    df_display = df_sample[cols_to_display].copy()
    
    # Format posted_date as string.
    df_display["POSTED_DATE"] = df_display["POSTED_DATE"].astype(str)
    
    # Generate HTML table with risk tooltips
    table_html = '<table border="1" style="border-collapse: collapse; width: 100%;">'
    table_html += "<tr>"
    
    # Table headers
    for col in df_display.columns:
        if col != "Risk_Explanation":  # Hide explanation column
            table_html += f'<th style="background-color: #0074D9; color: white; padding: 8px; text-align: left;">{col}</th>'
    table_html += "</tr>"
    
    # Table rows
    for _, row in df_display.iterrows():
        table_html += "<tr>"
        for col in df_display.columns:
            if col == "Risk":
                risk_html = risk_color_with_tooltip(row["Risk"], row["Risk_Explanation"])
                table_html += risk_html  # Add tooltip-enabled risk column
            elif col != "Risk_Explanation":
                table_html += f'<td style="padding: 8px;">{row[col]}</td>'
        table_html += "</tr>"
    
    table_html += "</table>"
    
    # Display table with fixed height scrolling
    st.markdown(f'<div style="height:600px; overflow-y: auto;">{table_html}</div>', unsafe_allow_html=True)
