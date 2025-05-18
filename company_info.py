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
    if "INDUSTRY" in companies_info.columns:
        industry_counts = companies_info["INDUSTRY"].value_counts().head(10).reset_index()
        industry_counts.columns = ["INDUSTRY", "Count"]
        fig_pie = px.pie(industry_counts, values="Count", names="INDUSTRY",
                         title="Industries Distribution",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_traces(textposition='outside', textinfo='label+percent', textfont=dict(size=12))
        fig_pie.update_layout(showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True, key="company_industry_pie")
    else:
        st.write("Industry column not found in companies data.")

    st.markdown("### Company Performance and Education/Skills Analysis (Based on Employee Profile)")

    
    # ------------------------
    # Chart 1: Top Companies by Average Salary (exclude companies with <10 postings)
    # ------------------------
    if "COMPANY_NAME" in df.columns and "AVG_SALARY" in df.columns:
        company_stats = df[df["AVG_SALARY"].notnull()].groupby("COMPANY_NAME").agg(
            avg_salary=("AVG_SALARY", "mean"),
            postings=("COMPANY_NAME", "count")
        ).reset_index()
        # Exclude companies with less than 10 postings.
        company_stats = company_stats[company_stats["postings"] >= 10]
        company_stats = company_stats.sort_values("avg_salary", ascending=False).head(20)
        height1 = max(300, len(company_stats)*30)
        fig_company_salary = px.bar(company_stats, x="avg_salary", y="COMPANY_NAME", orientation="h",
                                    title="Top Companies by Average Salary",
                                    labels={"COMPANY_NAME": "Company", "AVG_SALARY": "Average Salary"})
        fig_company_salary.update_yaxes(categoryorder="total ascending")
        fig_company_salary.update_layout(height=height1)
    else:
        fig_company_salary = None

    # ------------------------
    # Chart 2: Top Companies by Job Count
    # ------------------------
    if "COMPANY_NAME" in df.columns:
        job_count_company = df.groupby("COMPANY_NAME").size().reset_index(name="job_count")
        job_count_company = job_count_company.sort_values("job_count", ascending=False).head(20)
        height2 = max(300, len(job_count_company)*30)
        fig_company_job = px.bar(job_count_company, x="job_count", y="COMPANY_NAME", orientation="h",
                                 title="Top Companies by Job Count",
                                 labels={"COMPANY_NAME": "Company", "job_count": "Job Count"})
        fig_company_job.update_yaxes(categoryorder="total ascending")
        fig_company_job.update_layout(height=height2)
    else:
        fig_company_job = None

    # ------------------------
    # Chart 3: Top 20 Schools from "Where they studied"
    # ------------------------
    school_counts = {}
    if "WHERE_THEY_STUDIED" in companies_info.columns:
        for entry in companies_info["WHERE_THEY_STUDIED"].dropna():
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
    if "WHAT_THEY_ARE_SKILLED_AT" in companies_info.columns:
        for entry in companies_info["WHAT_THEY_ARE_SKILLED_AT"].dropna():
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
    
    st.markdown("### Entry-Level & Newbie-Friendly Companies")

    col_newbie, col_internship = st.columns(2)

    # ------------------------
    # Left: Most Newbie-Friendly Companies (MIN_YEARS_OF_EXPERIENCE == 0)
    # ------------------------
    with col_newbie:
        if "COMPANY_NAME" in df.columns and "MIN_YEARS_OF_EXPERIENCE" in df.columns:
            newbie_df = df[df["MIN_YEARS_OF_EXPERIENCE"] == 0]
            if not newbie_df.empty:
                newbie_counts = newbie_df.groupby("COMPANY_NAME").size().reset_index(name="newbie_job_count")
                newbie_counts = newbie_counts.sort_values("newbie_job_count", ascending=False).head(20)
                height_newbie = max(300, len(newbie_counts)*30)
                fig_newbie = px.bar(newbie_counts, x="newbie_job_count", y="COMPANY_NAME", orientation="h",
                                    title="Top Companies Hiring Inexperienced Graduates",
                                    labels={"COMPANY_NAME": "Company", "newbie_job_count": "Job Count"})
                fig_newbie.update_yaxes(categoryorder="total ascending")
                fig_newbie.update_layout(height=height_newbie)
                st.plotly_chart(fig_newbie, use_container_width=True, key="newbie_chart")
            else:
                st.write("No data available for companies hiring inexperienced graduates.")
        else:
            st.write("MIN_YEARS_OF_EXPERIENCE or COMPANY_NAME column not found in the job data.")

    # ------------------------
    # Right: Companies Hiring Internships & Entry Level (SENIORITY_LEVEL)
    # ------------------------
    with col_internship:
        if "COMPANY_NAME" in df.columns and "SENIORITY_LEVEL" in df.columns:
            internship_df = df[df["SENIORITY_LEVEL"].str.lower().isin(["internship", "entry level"])]
            if not internship_df.empty:
                internship_counts = internship_df.groupby("COMPANY_NAME").size().reset_index(name="internship_job_count")
                internship_counts = internship_counts.sort_values("internship_job_count", ascending=False).head(20)
                height_intern = max(300, len(internship_counts)*30)
                fig_internship = px.bar(internship_counts, x="internship_job_count", y="COMPANY_NAME", orientation="h",
                                        title="Top Companies Hiring Internship & Entry Level",
                                        labels={"COMPANY_NAME": "Company", "internship_job_count": "Job Count"})
                fig_internship.update_yaxes(categoryorder="total ascending")
                fig_internship.update_layout(height=height_intern)
                st.plotly_chart(fig_internship, use_container_width=True, key="internship_chart")
            else:
                st.write("No data available for Internship or Entry level positions.")
        else:
            st.write("SENIORITY_LEVEL or COMPANY_NAME column not found in the job data.")

    st.markdown("### Companies founded Over Time")
    if "FOUNDED" in companies_info.columns:
        companies_info["FOUNDED"] = pd.to_numeric(companies_info["FOUNDED"], errors="coerce")
        founded_data = companies_info.dropna(subset=["FOUNDED"])
        current_year = datetime.date.today().year
        founded_data = founded_data[(founded_data["FOUNDED"] >= 1900) & (founded_data["FOUNDED"] <= current_year)]
        founded_counts = founded_data.groupby("FOUNDED").size().reset_index(name="Count")
        founded_counts = founded_counts.sort_values("FOUNDED")
        fig_line = px.line(founded_counts, x="FOUNDED", y="Count",
                           title="Companies founded Over Time (1900-Present)",
                           markers=True)
        st.plotly_chart(fig_line, use_container_width=True, key="company_founded_line")
    else:
        st.write("founded column not found in companies data.")
