import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

def main(df, companies_info):
    st.header("Company Overview")
    
    # -------------------------------
    # Tile: Total Companies
    # -------------------------------
    total_companies = len(companies_info)
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
      <div style="font-size: 24px; font-weight: bold;">Total Companies</div>
      <div style="font-size: 48px;">{total_companies}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # -------------------------------
    # Pie Chart: Industries Distribution
    # -------------------------------
    st.markdown("### Industries Distribution")
    if "Industry" in companies_info.columns:
        industry_counts = companies_info["Industry"].value_counts().head(10).reset_index()
        industry_counts.columns = ["Industry", "Count"]
        fig_pie = px.pie(industry_counts, values="Count", names="Industry",
                         title="Industries Distribution",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_traces(textposition='outside', textinfo='label+percent', textfont=dict(size=12))
        fig_pie.update_layout(showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True, key="company_industry_pie")
    else:
        st.write("Industry column not found in companies data.")

    st.markdown("### Company Performance and Education/Skills Analysis")
    
    # ------------------------
    # Chart 1: Top Companies by Average Salary (exclude companies with <10 postings)
    # ------------------------
    if "company_name" in df.columns and "avg_salary" in df.columns:
        company_stats = df[df["avg_salary"].notnull()].groupby("company_name").agg(
            avg_salary=("avg_salary", "mean"),
            postings=("company_name", "count")
        ).reset_index()
        # Exclude companies with less than 10 postings.
        company_stats = company_stats[company_stats["postings"] >= 10]
        company_stats = company_stats.sort_values("avg_salary", ascending=False).head(20)
        height1 = max(300, len(company_stats)*30)
        fig_company_salary = px.bar(company_stats, x="avg_salary", y="company_name", orientation="h",
                                    title="Top Companies by Average Salary",
                                    labels={"company_name": "Company", "avg_salary": "Average Salary"})
        fig_company_salary.update_yaxes(categoryorder="total ascending")
        fig_company_salary.update_layout(height=height1)
    else:
        fig_company_salary = None

    # ------------------------
    # Chart 2: Top Companies by Job Count
    # ------------------------
    if "company_name" in df.columns:
        job_count_company = df.groupby("company_name").size().reset_index(name="job_count")
        job_count_company = job_count_company.sort_values("job_count", ascending=False).head(20)
        height2 = max(300, len(job_count_company)*30)
        fig_company_job = px.bar(job_count_company, x="job_count", y="company_name", orientation="h",
                                 title="Top Companies by Job Count",
                                 labels={"company_name": "Company", "job_count": "Job Count"})
        fig_company_job.update_yaxes(categoryorder="total ascending")
        fig_company_job.update_layout(height=height2)
    else:
        fig_company_job = None

    # ------------------------
    # Chart 3: Top 20 Schools from "Where they studied"
    # ------------------------
    school_counts = {}
    if "Where they studied" in companies_info.columns:
        for entry in companies_info["Where they studied"].dropna():
            try:
                school_list = ast.literal_eval(entry)
                if isinstance(school_list, list):
                    for item in school_list:
                        school, count = parse_entry(item)
                        if school:
                            school_counts[school] = school_counts.get(school, 0) + count
            except Exception:
                continue
        if school_counts:
            school_df = pd.DataFrame(list(school_counts.items()), columns=["School", "Count"])
            school_df = school_df.sort_values("Count", ascending=False).head(20)
            height3 = max(300, len(school_df)*30)
            fig_schools = px.bar(school_df, x="Count", y="School", orientation="h",
                                 title="Top 20 Schools",
                                 labels={"School": "School", "Count": "Head Count"})
            fig_schools.update_yaxes(categoryorder="total ascending")
            fig_schools.update_layout(height=height3)
        else:
            fig_schools = None
    else:
        fig_schools = None

    # ------------------------
    # Chart 4: Top 20 Skills from "What they are skilled at"
    # ------------------------
    skill_counts = {}
    if "What they are skilled at" in companies_info.columns:
        for entry in companies_info["What they are skilled at"].dropna():
            try:
                skill_list = ast.literal_eval(entry)
                if isinstance(skill_list, list):
                    for item in skill_list:
                        skill, count = parse_entry(item)
                        if skill:
                            skill_counts[skill] = skill_counts.get(skill, 0) + count
            except Exception:
                continue
        if skill_counts:
            skill_df = pd.DataFrame(list(skill_counts.items()), columns=["Skill", "Count"])
            skill_df = skill_df.sort_values("Count", ascending=False).head(20)
            height4 = max(300, len(skill_df)*30)
            fig_skills = px.bar(skill_df, x="Count", y="Skill", orientation="h",
                                title="Top 20 Skills",
                                labels={"Skill": "Skill", "Count": "Head Count"})
            fig_skills.update_yaxes(categoryorder="total ascending")
            fig_skills.update_layout(height=height4)
        else:
            fig_skills = None
    else:
        fig_skills = None

    # ------------------------
    # Arrange the four charts in a 2x2 matrix.
    # Left column: Chart 1 (salary) and Chart 3 (schools);
    # Right column: Chart 2 (job count) and Chart 4 (skills).
    col_left, col_right = st.columns(2)
    with col_left:
        if fig_company_salary is not None:
            st.plotly_chart(fig_company_salary, use_container_width=True, key="company_salary_chart")
        else:
            st.write("Company average salary data not available.")
        if fig_schools is not None:
            st.plotly_chart(fig_schools, use_container_width=True, key="schools_chart")
        else:
            st.write("School data not available.")
    with col_right:
        if fig_company_job is not None:
            st.plotly_chart(fig_company_job, use_container_width=True, key="company_job_chart")
        else:
            st.write("Company job count data not available.")
        if fig_skills is not None:
            st.plotly_chart(fig_skills, use_container_width=True, key="skills_chart")
        else:
            st.write("Skill data not available.")
    
    st.markdown("### Companies Founded Over Time")
    if "Founded" in companies_info.columns:
        companies_info["Founded"] = pd.to_numeric(companies_info["Founded"], errors="coerce")
        founded_data = companies_info.dropna(subset=["Founded"])
        current_year = datetime.date.today().year
        founded_data = founded_data[(founded_data["Founded"] >= 1900) & (founded_data["Founded"] <= current_year)]
        founded_counts = founded_data.groupby("Founded").size().reset_index(name="Count")
        founded_counts = founded_counts.sort_values("Founded")
        fig_line = px.line(founded_counts, x="Founded", y="Count",
                           title="Companies Founded Over Time (1900-Present)",
                           markers=True)
        st.plotly_chart(fig_line, use_container_width=True, key="company_founded_line")
    else:
        st.write("Founded column not found in companies data.")
    
# Example usage:
# companies_info = pd.read_csv("companies_info.csv")
# df = ...  # your job dataset
# main(df, companies_info)
