import streamlit as st

def main():
    st.header("Other Resources")

    st.markdown("### 🌐 External Resources")

    # Provide clickable external link
    st.markdown(
        """
        - [U.S. Bureau of Labor Statistics: Employment by Industry (Monthly Changes with Confidence Intervals)](https://www.bls.gov/charts/employment-situation/employment-by-industry-monthly-changes.htm)
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        - [U.S. Bureau of Labor Statistics: Employment by Industry (Monthly Changes)](https://www.bls.gov/charts/employment-situation/employment-by-industry-monthly-changes.htm)
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        - [U.S. Bureau of Labor Statistics: Employment and Average Hourly Earnings by Industry](https://www.bls.gov/charts/employment-situation/employment-by-industry-monthly-changes.htm)
        """,
        unsafe_allow_html=True
    )

    # Optional: show an image preview (if you prepare a local or static screenshot)
    # st.image("bls_screenshot.png", caption="BLS Monthly Employment Chart", use_column_width=True)
