import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import ast

# Helper function to create a pie chart with fixed, smaller dimensions.
def create_pie_chart(series, title, key_suffix, width=300, height=300, rotation=0, margin_top=60, font_size=10):
    counts = series.value_counts().head(10).reset_index()
    counts.columns = [series.name, 'count']
    fig = px.pie(counts, values='count', names=series.name, title=title)
    # Display label and percent outside with smaller font size.
    fig.update_traces(textposition='outside', textinfo='label+percent', textfont=dict(size=font_size))
    fig.update_layout(showlegend=False, width=width, height=height,
                      margin=dict(t=margin_top, b=20, l=20, r=20))
    if rotation:
        fig.update_traces(rotation=rotation)
    return fig

def main(df):
    st.header("Dataset Overview")
    
    # Ensure posted_date is datetime
    df['posted_date'] = pd.to_datetime(df['posted_date'], errors='coerce')

    # -------------------------------
    # Display Key Metrics
    # -------------------------------
    # total_jobs = len(df)
    # today = datetime.date.today()
    # jobs_today = df[df['posted_date'].dt.date == today].shape[0]
    # st.markdown(f"**Total Jobs Overall:** {total_jobs}  |  **Jobs Today:** {jobs_today}")
    total_jobs = len(df)
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
      <div style="font-size: 24px; font-weight: bold;">Total Number of Jobs</div>
      <div style="font-size: 48px;">{total_jobs}</div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------
    # Create 'interval' column using the full dataset (date only)
    # -------------------------------
    df['interval'] = df['posted_date'].dt.date

    # -------------------------------
    # Line Graph: Job Postings by Date (Smoothed)
    # -------------------------------
    st.markdown("### Number of Job Postings Over Time")
    job_count = df.groupby("interval").size().reset_index(name="job_count")
    job_count = job_count.sort_values("interval")
    fig_job_count = px.line(job_count, x="interval", y="job_count",
                            title="Job Postings by Date",
                            labels={"interval": "Date", "job_count": "Number of Postings"},
                            line_shape="spline")
    st.plotly_chart(fig_job_count, use_container_width=True, key="job_count_chart")

    # -------------------------------
    # Line Graph: Average Salary by Date (Smoothed)
    # -------------------------------
    st.markdown("### Average Salary Over Time")
    salary_over_time = df[df['avg_salary'].notnull()].groupby("interval")['avg_salary'].mean().reset_index(name="avg_salary")
    salary_over_time = salary_over_time.sort_values("interval")
    fig_salary_trend = px.line(salary_over_time, x="interval", y="avg_salary",
                               title="Average Salary by Date",
                               labels={"interval": "Date", "avg_salary": "Average Salary"},
                               line_shape="spline")
    st.plotly_chart(fig_salary_trend, use_container_width=True, key="salary_trend_chart")

    # -------------------------------
    # Histogram: Salary Distribution (0 - 500,000)
    # -------------------------------
    # st.markdown("### Salary Distribution")
    salary_data = df[(df['avg_salary'].notnull()) & (df['avg_salary']>=0) & (df['avg_salary']<=500000)]
    fig_salary_hist = px.histogram(salary_data, x="avg_salary", nbins=50,
                                   title="Salary Distribution",
                                   labels={"avg_salary": "Salary"},
                                   range_x=[0,500000])
    # st.plotly_chart(fig_salary_hist, use_container_width=True, key="salary_hist_chart")

    # -------------------------------
    # Pie Charts for Categorical Data in a 3x2 Matrix
    # -------------------------------
    st.markdown("### Categorical Distributions")
    
    # Pie Chart: Seniority Level
    if 'seniority_level' in df.columns:
        fig_seniority = create_pie_chart(df['seniority_level'], "Seniority Level Distribution", "pie_seniority")
    else:
        fig_seniority = None

    # Pie Chart: Workplace
    if 'workplace' in df.columns:
        fig_workplace = create_pie_chart(df['workplace'], "Workplace Distribution", "pie_workplace")
    else:
        fig_workplace = None

    # Pie Chart: Employment Type (rotate by 90° to avoid overlap)
    if 'employment_type' in df.columns:
        fig_emp_type = create_pie_chart(df['employment_type'], "Employment Type Distribution", "pie_employment", rotation=90, margin_top=60, font_size=10)
    else:
        fig_emp_type = None

    # Pie Chart: Job Function (from job_function_list)
    if 'job_function_list' in df.columns:
        all_job_funcs = []
        for item in df['job_function_list'].dropna():
            try:
                funcs = ast.literal_eval(item)
                if isinstance(funcs, list):
                    all_job_funcs.extend(funcs)
            except Exception:
                continue
        if all_job_funcs:
            job_func_series = pd.Series(all_job_funcs, name="job_function")
            fig_job_func = create_pie_chart(job_func_series, "Job Function Distribution", "pie_job_func")
        else:
            fig_job_func = None
    else:
        fig_job_func = None

    # Pie Chart: Industry (from industries_list)
    if 'industries_list' in df.columns:
        all_industries = []
        for item in df['industries_list'].dropna():
            try:
                inds = ast.literal_eval(item)
                if isinstance(inds, list):
                    all_industries.extend(inds)
            except Exception:
                continue
        if all_industries:
            industry_series = pd.Series(all_industries, name="industry")
            fig_industry = create_pie_chart(industry_series, "Industry Distribution", "pie_industry")
        else:
            fig_industry = None
    else:
        fig_industry = None

    # -------------------------------
    # Arrange the 6 charts in a 3x2 matrix:
    # Row 1: Salary Distribution (left), Seniority Level (right)
    # Row 2: Workplace (left), Employment Type (right)
    # Row 3: Job Function (left), Industry (right)
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    row3_col1, row3_col2 = st.columns(2)

    with row1_col1:
        st.plotly_chart(fig_salary_hist, use_container_width=True, key="salary_hist_chart_matrix")
    with row1_col2:
        if fig_seniority is not None:
            st.plotly_chart(fig_seniority, use_container_width=True, key="pie_seniority_chart")
        else:
            st.write("Seniority data not available.")
    
    with row2_col1:
        if fig_workplace is not None:
            st.plotly_chart(fig_workplace, use_container_width=True, key="pie_workplace_chart")
        else:
            st.write("Workplace data not available.")
    with row2_col2:
        if fig_emp_type is not None:
            st.plotly_chart(fig_emp_type, use_container_width=True, key="pie_employment_chart")
        else:
            st.write("Employment type data not available.")
    
    with row3_col1:
        if fig_job_func is not None:
            st.plotly_chart(fig_job_func, use_container_width=True, key="pie_job_func_chart")
        else:
            st.write("Job function data not available.")
    with row3_col2:
        if fig_industry is not None:
            st.plotly_chart(fig_industry, use_container_width=True, key="pie_industry_chart")
        else:
            st.write("Industry data not available.")

# Example usage:
# Call main(df) where df is your DataFrame.
