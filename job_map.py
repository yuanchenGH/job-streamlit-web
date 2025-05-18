import streamlit as st
import plotly.express as px
import pandas as pd

# Cache processed job data to avoid recomputation
@st.cache_data
def process_data(df, state_df, city_df):
    """Preprocess job data and aggregate metrics for faster loading."""

    # --------------------------------
    # ✅ Step 1: Aggregate job data
    # --------------------------------
    # STATE-LEVEL Aggregation
    # STATE-LEVEL Aggregation (Sorted by JOB_COUNT)
    state_agg = df.groupby("STATE").agg(
        JOB_COUNT=("JOB_ID", "count"),
        AVG_SALARY=("AVG_SALARY", "mean")
    ).reset_index().sort_values(by="JOB_COUNT", ascending=False)

    # CITY-LEVEL Aggregation (Sorted by JOB_COUNT)
    city_agg = df.groupby("LOCATION").agg(
        JOB_COUNT=("JOB_ID", "count")
    ).reset_index().sort_values(by="JOB_COUNT", ascending=False)

    # --------------------------------
    # ✅ Step 2: Join State Data (AFTER Aggregation)
    # --------------------------------
    state_agg = state_agg.merge(
        state_df[["STATE", "STATE_LATITUDE", "STATE_LONGITUDE", "POPULATION", "COST_INDEX"]],
        on="STATE", how="left"
    )

    # --------------------------------
    # ✅ Step 3: Join City Data (AFTER Aggregation)
    # --------------------------------
    city_agg = city_agg.merge(
        city_df[["LOCATION", "LATITUDE", "LONGITUDE"]].drop_duplicates(),
        on="LOCATION", how="left"
    )

    # --------------------------------
    # ✅ Step 4: Compute Adjusted Metrics
    # --------------------------------
    # Adjusted Job Count by Population (Global normalization)
    overall_mean_pop = state_agg["POPULATION"].mean()
    state_agg["ADJUSTED_JOB_COUNT"] = state_agg["JOB_COUNT"] * (overall_mean_pop / state_agg["POPULATION"])

    # Adjusted Salary by Cost of Living
    state_agg["ADJUSTED_AVG_SALARY"] = state_agg.apply(
        lambda row: row["AVG_SALARY"] * (100 / row["COST_INDEX"]) if row["COST_INDEX"] > 0 else row["AVG_SALARY"],
        axis=1
    )

    return state_agg, city_agg

def main(df, state_df, city_df):
    st.header("Job Density Map")

    # Process Data (cached)
    state_agg, city_agg = process_data(df, state_df, city_df)

    # --- Map Section ---
    map_type = st.selectbox("Select Map Type", ["State-Level", "City-Level"])
    zoom_level = 4 if df['STATE'].nunique() == 1 else 3

    if map_type == "State-Level":
        if state_agg.empty:
            st.warning("No data available for state-level analysis.")
        else:
            fig_map = px.scatter_mapbox(
                state_agg.dropna(subset=["STATE_LATITUDE", "STATE_LONGITUDE"]),
                lat="STATE_LATITUDE",
                lon="STATE_LONGITUDE",
                size="JOB_COUNT",
                color="STATE",
                hover_name="STATE",
                title="Job Density by State",
                zoom=zoom_level,
                opacity=0.7,
                size_max=35
            )
            fig_map.update_layout(mapbox_style="carto-positron", showlegend=False)
            st.plotly_chart(fig_map, use_container_width=True)
    else:
        if city_agg.empty:
            st.warning("No city-level data available.")
        else:
            city_agg_100 = city_agg.head(100)
            fig_map = px.scatter_mapbox(
                city_agg_100.dropna(subset=["LATITUDE", "LONGITUDE"]),
                lat="LATITUDE",
                lon="LONGITUDE",
                size="JOB_COUNT",
                color="LOCATION",
                hover_name="LOCATION",
                title="Job Density by City",
                zoom=zoom_level,
                opacity=0.7,
                size_max=20
            )
            fig_map.update_layout(mapbox_style="carto-positron", showlegend=False)
            st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("### Top Locations Analysis")
    group_key = "STATE" if map_type == "State-Level" else "LOCATION"

    # ------------------------
    # Chart 1: Top by Job Counts (Filtered)
    # ------------------------
    top_job_count = state_agg[["STATE", "JOB_COUNT"]].sort_values("JOB_COUNT", ascending=False).head(20)
    fig1 = px.bar(top_job_count, x="JOB_COUNT", y="STATE", orientation='h',
                  title="Top States by Job Counts",
                  color_discrete_sequence=px.colors.qualitative.Plotly)
    fig1.update_yaxes(categoryorder="total ascending")
    fig1.update_layout(height=max(200, len(top_job_count) * 30))

    # ------------------------
    # Chart 2: Top by Average Salary (Filtered)
    # ------------------------
    top_avg_salary = state_agg[["STATE", "AVG_SALARY"]].dropna().sort_values("AVG_SALARY", ascending=False).head(20)
    fig2 = px.bar(top_avg_salary, x="AVG_SALARY", y="STATE", orientation='h',
                  title="Top States by Average Salary",
                  color_discrete_sequence=px.colors.qualitative.Plotly)
    fig2.update_yaxes(categoryorder="total ascending")
    fig2.update_layout(height=max(200, len(top_avg_salary) * 30))

    # ------------------------
    # Chart 3: Job Counts Adjusted by Population
    # ------------------------
    top_adj_jobs = state_agg[["STATE", "ADJUSTED_JOB_COUNT"]].dropna().sort_values("ADJUSTED_JOB_COUNT", ascending=False).head(20)
    fig3 = px.bar(top_adj_jobs, x="ADJUSTED_JOB_COUNT", y="STATE", orientation='h',
                  title="Top States by Job Counts - Adjusted by Population",
                  color_discrete_sequence=["lightblue"])
    fig3.update_yaxes(categoryorder="total ascending")
    fig3.update_layout(height=max(200, len(top_adj_jobs) * 30))

    # ------------------------
    # Chart 4: Average Salary Adjusted by Cost of Living
    # ------------------------
    top_adj_salary = state_agg[["STATE", "ADJUSTED_AVG_SALARY"]].dropna().sort_values("ADJUSTED_AVG_SALARY", ascending=False).head(20)
    fig4 = px.bar(top_adj_salary, x="ADJUSTED_AVG_SALARY", y="STATE", orientation='h',
                  title="Top States by Average Salary - Adjusted by Cost of Living",
                  color_discrete_sequence=["lightblue"])
    fig4.update_yaxes(categoryorder="total ascending")
    fig4.update_layout(height=max(200, len(top_adj_salary) * 30))

    # ------------------------
    # Layout: Arrange the four charts in a 2x2 grid.
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        st.plotly_chart(fig3, use_container_width=True)
        st.plotly_chart(fig4, use_container_width=True)
