import streamlit as st
import plotly.express as px

def main(df):
    st.header("Job Density Map")
    
    # --- Map Section ---
    map_type = st.selectbox("Select Map Type", ["State-Level", "City-Level"])
    zoom_level = 4 if df['state'].nunique() == 1 else 3

    if map_type == "State-Level":
        state_data = df.groupby("state").size().reset_index(name="count")
        state_data = state_data.merge(
            df[["state", "state_latitude", "state_longitude"]].drop_duplicates(), 
            on="state", how="left"
        )
        state_data = state_data.dropna(subset=["state_latitude", "state_longitude"])
        if state_data.empty:
            st.warning("No data available for state-level analysis.")
        else:
            fig_map = px.scatter_map(
                state_data,
                lat="state_latitude",
                lon="state_longitude",
                size="count",
                color="state",
                hover_name="state",
                title="Job Density by State",
                zoom=zoom_level,
                opacity=0.7,
                size_max=35
            )
            fig_map.update_layout(showlegend=False)
            st.plotly_chart(fig_map, use_container_width=True)
    else:
        city_data = df.groupby(["location_st", "latitude", "longitude"]).size().reset_index(name="count")
        city_data = city_data.dropna(subset=["latitude", "longitude"])
        city_data = city_data.sort_values(by="count", ascending=False).head(200)
        if city_data.empty:
            st.warning("No city-level data available.")
        else:
            fig_map = px.scatter_map(
                city_data,
                lat="latitude",
                lon="longitude",
                size="count",
                color="location_st",
                hover_name="location_st",
                title="Job Density by City",
                zoom=zoom_level,
                opacity=0.7,
                size_max=20
            )
            fig_map.update_layout(showlegend=False, width=800, height=600)
            st.plotly_chart(fig_map, use_container_width=False)
    
    st.markdown("### Top Locations Analysis")
    
    # Determine grouping key based on map type.
    group_key = "state" if map_type == "State-Level" else "location_st"
    
    # ------------------------
    # Chart 1: Top by Job Counts (Filtered)
    # ------------------------
    counts_df = df.groupby(group_key).agg(job_count=("job_id", "count")).reset_index()
    counts_df = counts_df.sort_values("job_count", ascending=False).head(20)
    fig1 = px.bar(counts_df, x="job_count", y=group_key, orientation='h',
                  title="Top State by Job Counts",
                  color_discrete_sequence=px.colors.qualitative.Plotly)
    fig1.update_yaxes(categoryorder="total ascending")
    height1 = max(200, len(counts_df)*30)
    fig1.update_layout(height=height1)
    
    # ------------------------
    # Chart 2: Top by Average Salary (Filtered)
    # ------------------------
    salary_df = df[df["avg_salary"].notnull()].groupby(group_key).agg(avg_salary=("avg_salary", "mean")).reset_index()
    salary_df = salary_df.sort_values("avg_salary", ascending=False).head(20)
    fig2 = px.bar(salary_df, x="avg_salary", y=group_key, orientation='h',
                  title="Top State by Average Salary",
                  color_discrete_sequence=px.colors.qualitative.Plotly)
    fig2.update_yaxes(categoryorder="total ascending")
    height2 = max(200, len(salary_df)*30)
    fig2.update_layout(height=height2)
    
    # ------------------------
    # Chart 3: Job Counts Adjusted by Population (Global)
    # ------------------------
    pop_df = df.groupby(group_key).agg(job_count=("job_id", "count"),
                                        population=("population", "mean")).reset_index()
    overall_mean_pop = pop_df["population"].mean()
    pop_df["adjusted_job_count"] = pop_df["job_count"] * (overall_mean_pop / pop_df["population"])
    pop_df = pop_df.sort_values("adjusted_job_count", ascending=False).head(20)
    fig3 = px.bar(pop_df, x="adjusted_job_count", y=group_key, orientation='h',
                  title="Top State by Job Counts - Adjusted by Population",
                  color_discrete_sequence=["lightblue"])
    fig3.update_yaxes(categoryorder="total ascending")
    height3 = max(200, len(pop_df)*30)
    fig3.update_layout(height=height3)
    
    # ------------------------
    # Chart 4: Average Salary Adjusted by Cost Index (Global)
    # ------------------------
    cost_df = df[df["avg_salary"].notnull()].groupby(group_key).agg(
                avg_salary=("avg_salary", "mean"),
                cost_index=("cost_index", "mean")
              ).reset_index()
    cost_df["adjusted_avg_salary"] = cost_df.apply(
        lambda row: row["avg_salary"] * (100 / row["cost_index"]) if row["cost_index"] > 0 else row["avg_salary"],
        axis=1
    )
    cost_df = cost_df.sort_values("adjusted_avg_salary", ascending=False).head(20)
    fig4 = px.bar(cost_df, x="adjusted_avg_salary", y=group_key, orientation='h',
                  title="Top State by Average Salary - Adjusted by Cost of Living",
                  color_discrete_sequence=["lightblue"])
    fig4.update_yaxes(categoryorder="total ascending")
    height4 = max(200, len(cost_df)*30)
    fig4.update_layout(height=height4)
    
    # ------------------------
    # Layout: Arrange the four charts in a 2x2 grid.
    # Left column: Chart 1 and Chart 3; Right column: Chart 2 and Chart 4.
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        st.plotly_chart(fig3, use_container_width=True)
        st.plotly_chart(fig4, use_container_width=True)
