import streamlit as st
import pandas as pd
import plotly.express as px
import ast

# Helper function to create a pie chart with fixed, smaller dimensions.
def create_pie_chart(series, title, key_suffix, width=300, height=300, rotation=0, margin_top=60, font_size=10):
    counts = series.value_counts().head(10).reset_index()
    counts.columns = [series.name, 'COUNT']
    fig = px.pie(counts, values='COUNT', names=series.name, title=title)
    # Display label and percent outside with smaller font size.
    fig.update_traces(textposition='outside', textinfo='label+percent', textfont=dict(size=font_size))
    fig.update_layout(showlegend=False, width=width, height=height,
                      margin=dict(t=margin_top, b=20, l=20, r=20))
    if rotation:
        fig.update_traces(rotation=rotation)
    return fig

def main(df):
    st.header("Dataset Overview")
    
    # Ensure POSTED_DATE is datetime
    # df['POSTED_DATE'] = pd.to_datetime(df['POSTED_DATE'], errors='coerce')

    # -------------------------------
    # Display Key Metrics
    # -------------------------------
    total_jobs = len(df)
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
      <div style="font-size: 24px; font-weight: bold;">Total Number of Jobs</div>
      <div style="font-size: 48px;">{total_jobs}</div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------
    # Create 'INTERVAL' column using the full dataset (date only)
    # -------------------------------
    df['INTERVAL'] = df['POSTED_DATE'].dt.date
    sampled_df = df.groupby('POSTED_DATE').apply(lambda x: x.sample(frac=0.1, random_state=42)).reset_index(drop=True)

    # -------------------------------
    # Line Graph: Job Postings by Date (Smoothed)
    # -------------------------------
    st.markdown("### Number of Job Postings Over Time")
    job_count = df.groupby("INTERVAL").size().reset_index(name="JOB_COUNT")
    job_count = job_count.sort_values("INTERVAL")
    fig_job_count = px.line(job_count, x="INTERVAL", y="JOB_COUNT",
                            title="Job Postings by Date",
                            labels={"INTERVAL": "Date", "JOB_COUNT": "Number of Postings"},
                            line_shape="spline")
    st.plotly_chart(fig_job_count, use_container_width=True, key="job_count_chart")

    # -------------------------------
    # Line Graph: Average Salary by Date (Smoothed)
    # -------------------------------
    st.markdown("### Average Salary Over Time")
    # salary_data = df[(df['AVG_SALARY']>=20000) & (df['AVG_SALARY']<=500000)]
    # salary_over_time = df.groupby("INTERVAL")['AVG_SALARY'].mean().reset_index(name="AVG_SALARY")
    salary_over_time = sampled_df.groupby("INTERVAL")['AVG_SALARY'].mean().reset_index(name="AVG_SALARY")
    salary_over_time = salary_over_time.sort_values("INTERVAL")
    fig_salary_trend = px.line(salary_over_time, x="INTERVAL", y="AVG_SALARY",
                               title="Average Salary by Date",
                               labels={"INTERVAL": "Date", "AVG_SALARY": "Average Salary"},
                               line_shape="spline")
    st.plotly_chart(fig_salary_trend, use_container_width=True, key="salary_trend_chart")

    # -------------------------------
    # Histogram: Salary Distribution (0 - 500,000)
    # -------------------------------
    # salary_data = df[(df['AVG_SALARY']>=20000) & (df['AVG_SALARY']<=500000)]
    fig_salary_hist = px.histogram(df, x="AVG_SALARY", nbins=50,
                                   title="Salary Distribution",
                                   labels={"AVG_SALARY": "Salary"},
                                   range_x=[20000,500000])

    # -------------------------------
    # Pie Charts for Categorical Data in a 3x2 Matrix
    # -------------------------------
    st.markdown("### Categorical Distributions")
    
    # Pie Chart: Seniority Level
    if 'SENIORITY_LEVEL' in df.columns:
        # fig_seniority = create_pie_chart(df['SENIORITY_LEVEL'], "Seniority Level Distribution", "pie_seniority")
        fig_seniority = create_pie_chart(sampled_df['SENIORITY_LEVEL'], "Seniority Level Distribution", "pie_seniority")
    else:
        fig_seniority = None

    # Pie Chart: Workplace
    if 'WORKPLACE' in df.columns:
        # fig_workplace = create_pie_chart(df['WORKPLACE'], "Workplace Distribution", "pie_workplace")
        fig_workplace = create_pie_chart(sampled_df['WORKPLACE'], "Workplace Distribution", "pie_workplace")
    else:
        fig_workplace = None

    # Pie Chart: Employment Type (rotate by 90° to avoid overlap)
    if 'EMPLOYMENT_TYPE' in df.columns:
        # fig_emp_type = create_pie_chart(df['EMPLOYMENT_TYPE'], "Employment Type Distribution", "pie_employment", rotation=90, margin_top=60, font_size=10)
        fig_emp_type = create_pie_chart(sampled_df['EMPLOYMENT_TYPE'], "Employment Type Distribution", "pie_employment", rotation=90, margin_top=60, font_size=10)
    else:
        fig_emp_type = None

    # Pie Chart: Job Function (from JOB_FUNCTION_LIST)
    # if 'JOB_FUNCTION_LIST' in df.columns:
    #     all_job_funcs = []
    #     # for item in df['JOB_FUNCTION_LIST'].dropna():
    #     for item in sampled_df['JOB_FUNCTION_LIST'].dropna():
    #         try:
    #             funcs = ast.literal_eval(item)
    #             if isinstance(funcs, list):
    #                 all_job_funcs.extend(funcs)
    #         except Exception:
    #             continue
    #     if all_job_funcs:
    #         job_func_series = pd.Series(all_job_funcs, name="JOB_FUNCTION")
    #         fig_job_func = create_pie_chart(job_func_series, "Job Function Distribution", "pie_job_func")
    #     else:
    #         fig_job_func = None
    # else:
    #     fig_job_func = None

    # Pie Chart: Job Function (from JOB_FUNCTION_LIST)
    if 'JOB_FUNCTION_LIST' in sampled_df.columns:
        exploded_job_funcs = (
            sampled_df['JOB_FUNCTION_LIST']
            .dropna()
            .apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
            .explode()
            .dropna()
        )

        if not exploded_job_funcs.empty:
            job_func_series = exploded_job_funcs.rename("JOB_FUNCTION")
            fig_job_func = create_pie_chart(job_func_series, "Job Function Distribution", "pie_job_func")
        else:
            fig_job_func = None
    else:
        fig_job_func = None


    # -------------------------------
    # Arrange the 6 charts in a 3x2 matrix:
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
