import pandas as pd
import streamlit as st
import plotly.express as px
import os

# -------------------------
# Load and prepare data
# -------------------------

# Get the folder where app.py is located
base_dir = os.path.dirname(os.path.abspath(__file__))

# Build the relative path to the CSV
csv_path = os.path.join(base_dir, "Production_Crops_E_Americas.csv")

# Read the CSV file
crop_data = pd.read_csv(csv_path, encoding='latin-1')


#crop_data = pd.read_csv("C:/Users/k_lei/Documents/america_crop_production/america_crop_production/Production_Crops_E_Americas.csv", encoding='latin-1') 

# Filter by element
production = crop_data[crop_data['Element'] == 'Production'].copy()
area = crop_data[crop_data['Element'] == 'Area harvested'].copy()
yield_ = crop_data[crop_data['Element'] == 'Yield'].copy()

# Extract year columns
years = [col for col in production.columns if col.startswith('Y') and not col.endswith('F')]

def melt_element(df, element_name, unit, desc):
    df_long = df.melt(
        id_vars=['Area','Item'], 
        value_vars=years,
        var_name='Year',
        value_name='Value'
    )
    df_long['Year'] = df_long['Year'].str[1:].astype(int)
    df_long['Value'] = pd.to_numeric(df_long['Value'], errors='coerce')
    df_long['Element'] = element_name
    df_long['Unit'] = unit
    df_long['Description'] = desc
    return df_long

production_long = melt_element(production, "Production", "Tonnes", "Total produced")
area_long = melt_element(area, "Area harvested", "ha", "Area used for harvest")
yield_long = melt_element(yield_, "Yield", "Hg/ha", "Production to area ratio")

df_long = pd.concat([production_long, area_long, yield_long], ignore_index=True)
df_long.dropna(subset=["Value"], inplace=True)
df_long.rename(columns={"Area":"Country"}, inplace=True)

# -------------------------
# Streamlit Interface
# -------------------------
st.title("📊 Agricultural Production Explorer in the Americas")
st.write("Interactive visualization of data from the Food and Agriculture Organization of the United Nations (FAO).")


tab1, tab2 = st.tabs(["Yearly Distribution", "Temporal Trend"])

with tab1:
    st.subheader("Yearly Distribution - all countries")

    year_hist = st.slider(
        "Select year:",
        int(df_long["Year"].min()),
        int(df_long["Year"].max()),
        value=int(df_long["Year"].max())
    )
    element_hist = st.selectbox(
        "Variable:",
        ["Production","Area harvested"], 
        key="element_hist2"
    )

    # Chart selection
    show_hist = st.checkbox("Show Histogram")
    show_scatter = st.checkbox("Show Scatter Plot")

    if st.button("Generate chart by year", key="btn_hist_year"):
        filtered_hist = df_long[
            (df_long["Year"] == year_hist) &
            (df_long["Element"] == element_hist)
        ]

        if filtered_hist.empty:
            st.warning("No data available for this year and variable.")
        else:
            title_base = f"{filtered_hist['Description'].iloc[0]} in {year_hist} [{filtered_hist['Unit'].iloc[0]}]"

            if not show_hist and not show_scatter:
                st.warning("Please select at least one chart type.")
            else:
                if show_hist:
                    fig_hist = px.histogram(
                        filtered_hist,
                        x="Country",
                        y="Value",
                        color="Country",
                        title="Histogram - " + title_base
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)

                if show_scatter:
                    fig_scatter = px.scatter(
                        filtered_hist,
                        x="Country",
                        y="Value",
                        color="Country",
                        size="Value",
                        title="Scatter Plot - " + title_base
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)


# =====================================
# TAB 2: Temporal Trend
# =====================================
with tab2:
    st.subheader("Temporal trend comparison")

    countries_line = st.multiselect("Country(ies) to compare:", sorted(df_long["Country"].unique()), default=["Costa Rica"])
    crop_line = st.selectbox("Crop:", sorted(df_long["Item"].unique()), key="crop_line")
    element_line = st.selectbox("Variable:", ["Production","Area harvested","Yield"], key="element_line")

    if st.button("Generate temporal trend"):
        trend_data = df_long[
            (df_long["Country"].isin(countries_line)) &
            (df_long["Item"]==crop_line) &
            (df_long["Element"]==element_line)
        ]

        if trend_data.empty:
            st.warning("No data available for this combination.")
        else:
            title = f"{trend_data['Description'].iloc[0]} of {crop_line} [{trend_data['Unit'].iloc[0]}]"
            fig = px.line(trend_data, x="Year", y="Value", color="Country", markers=True, title=title)
            st.plotly_chart(fig, use_container_width=True)
