import streamlit as st
import pandas as pd
import plotly.express as px
import ast

def main(df):
    st.header("Requirements Overview")
    
    # -------------------------------
    # Top 10 Degrees and Top 10 Skills Side by Side (Horizontal Bars)
    # -------------------------------
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Top 10 Degrees")
        if 'degree' in df.columns:
            # Count degrees, select the top 10 highest, then sort them in ascending order.
            degree_counts = df['degree'].value_counts().head(10).sort_values(ascending=True)
            degree_counts = degree_counts.reset_index()
            degree_counts.columns = ['degree', 'count']
            # Create horizontal bar chart.
            fig_degree = px.bar(degree_counts, x='count', y='degree', 
                                orientation='h',
                                title='Degree Distribution',
                                labels={'degree': 'Degree', 'count': 'Count'})
            st.plotly_chart(fig_degree, use_container_width=True)
        else:
            st.write("Column 'degree' not found in the data.")
            
    with col2:
        st.markdown("### Top 10 Skills Frequency")
        if 'skills_clean' in df.columns:
            all_skills = []
            for item in df['skills_clean'].dropna():
                try:
                    # Convert string representation of list to an actual list.
                    skills = ast.literal_eval(item)
                    if isinstance(skills, list):
                        all_skills.extend(skills)
                except Exception:
                    continue
            
            if all_skills:
                skills_series = pd.Series(all_skills)
                # Select top 10 highest, then sort in ascending order.
                skills_counts = skills_series.value_counts().head(10).sort_values(ascending=True)
                skills_counts = skills_counts.reset_index()
                skills_counts.columns = ['skill', 'count']
                # Create horizontal bar chart.
                fig_skills = px.bar(skills_counts, x='count', y='skill', 
                                    orientation='h',
                                    title='Skills Frequency',
                                    labels={'skill': 'Skill', 'count': 'Count'})
                st.plotly_chart(fig_skills, use_container_width=True)
            else:
                st.write("No skills data available after processing.")
        else:
            st.write("Column 'skills_clean' not found in the data.")
    
    # -------------------------------
    # Minimum Years of Experience Chart (0-20) as Vertical Bars
    # -------------------------------
    st.markdown("### Minimum Years of Experience Distribution (0-20)")
    if 'min_years_of_experience' in df.columns:
        # Filter for values between 0 and 20.
        # Filter for values between 0 and 20 and convert to integers
        df_exp = df[(df['min_years_of_experience'] >= 0) & (df['min_years_of_experience'] <= 20)].copy()
        df_exp['years'] = df_exp['min_years_of_experience'].astype(int)  # or use .round().astype(int) if you prefer

        exp_counts = df_exp['years'].value_counts().reset_index()
        exp_counts.columns = ['years', 'count']
        exp_counts = exp_counts.sort_values(by="years")
        fig_exp = px.bar(exp_counts, x='years', y='count', 
                        title='Minimum Years of Experience Distribution (0-20)',
                        labels={'years': 'Years of Experience', 'count': 'Count'})
        st.plotly_chart(fig_exp, use_container_width=True)
    else:
        st.write("Column 'min_years_of_experience' not found in the data.")
