import streamlit as st
import pandas as pd
import plotly.express as px
import ast

def main(df):
    st.header("Requirements Overview (Based on Job Description)")
    sampled_df = df.groupby('POSTED_DATE').apply(lambda x: x.sample(frac=0.1, random_state=42)).reset_index(drop=True)
    
    # -------------------------------
    # Top 10 Degrees and Top 10 Skills Side by Side (Horizontal Bars)
    # -------------------------------
    col1, col2 = st.columns(2)
    
    # with col1:
    #     st.markdown("### Top 10 Degrees")
    #     if 'DEGREE' in sampled_df.columns:
    #         # Count degrees, select the top 10 highest, then sort them in ascending order.
    #         degree_counts = sampled_df['DEGREE'].value_counts().head(10).sort_values(ascending=True)
    #         degree_counts = degree_counts.reset_index()
    #         degree_counts.columns = ['degree', 'count']
    #         # Create horizontal bar chart.
    #         fig_degree = px.bar(degree_counts, x='count', y='degree', 
    #                             orientation='h',
    #                             title='Degree Distribution',
    #                             labels={'degree': 'Degree', 'count': 'Count'})
    #         st.plotly_chart(fig_degree, use_container_width=True)
    #     else:
    #         st.write("Column 'degree' not found in the data.")

    with col1:
        st.markdown("### Top 10 Degrees")
        if 'DEGREE' in sampled_df.columns:
            # Drop true NaN + remove blanks and 'nan' strings
            valid_degrees = (
                sampled_df['DEGREE']
                .dropna()  # remove true NaNs
                .astype(str)
                .str.strip()
            )
            # Filter out empty strings and 'nan' string (case-insensitive)
            valid_degrees = valid_degrees[valid_degrees.str.lower() != 'nan']
            valid_degrees = valid_degrees[valid_degrees != '']

            # Count top 10
            degree_counts = (
                valid_degrees
                .value_counts()
                .head(10)
                .sort_values(ascending=True)
                .reset_index()
            )
            degree_counts.columns = ['degree', 'count']

            if not degree_counts.empty:
                # Create horizontal bar chart.
                fig_degree = px.bar(
                    degree_counts, x='count', y='degree',
                    orientation='h',
                    title='Degree Distribution',
                    labels={'degree': 'Degree', 'count': 'Count'}
                )
                st.plotly_chart(fig_degree, use_container_width=True)
            else:
                st.write("No valid degree data available.")
        else:
            st.write("Column 'DEGREE' not found in the data.")


            
    with col2:
        st.markdown("### Top 10 Skills Frequency")
        if 'SKILLS_MATCHED' in sampled_df.columns:
            all_skills = []
            for item in sampled_df['SKILLS_MATCHED'].dropna():
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
    if 'MIN_YEARS_OF_EXPERIENCE' in sampled_df.columns:
        # Filter for values between 0 and 20.
        # Filter for values between 0 and 20 and convert to integers
        df_exp = sampled_df[(sampled_df['MIN_YEARS_OF_EXPERIENCE'] >= 0) & (sampled_df['MIN_YEARS_OF_EXPERIENCE'] <= 20)].copy()
        df_exp['years'] = df_exp['MIN_YEARS_OF_EXPERIENCE'].astype(int)  # or use .round().astype(int) if you prefer

        exp_counts = df_exp['years'].value_counts().reset_index()
        exp_counts.columns = ['years', 'count']
        exp_counts = exp_counts.sort_values(by="years")
        fig_exp = px.bar(exp_counts, x='years', y='count', 
                        title='Minimum Years of Experience Distribution (0-20)',
                        labels={'years': 'Years of Experience', 'count': 'Count'})
        st.plotly_chart(fig_exp, use_container_width=True)
    else:
        st.write("Column 'min_years_of_experience' not found in the data.")
