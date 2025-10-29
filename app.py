import pandas as pd
import streamlit as st
import plotly.express as px

# -------------------------
# Cargar y preparar datos
# -------------------------
crop_data = pd.read_csv("C:/Users/k_lei/Documents/america_crop_production/america_crop_production/Production_Crops_E_Americas.csv", encoding='latin-1') 

# Filtrar por elemento
production = crop_data[crop_data['Element'] == 'Production'].copy()
area = crop_data[crop_data['Element'] == 'Area harvested'].copy()
yield_ = crop_data[crop_data['Element'] == 'Yield'].copy()

# Extraer columnas de años
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

production_long = melt_element(production, "Production", "Tonnes", "Total producido")
area_long = melt_element(area, "Area harvested", "ha", "Área utilizada para cosecha")
yield_long = melt_element(yield_, "Yield", "Hg/ha", "Relación producción / área")

df_long = pd.concat([production_long, area_long, yield_long], ignore_index=True)
df_long.dropna(subset=["Value"], inplace=True)
df_long.rename(columns={"Area":"Country"}, inplace=True)

# -------------------------
# Interfaz de Streamlit
# -------------------------
st.title("📊 Explorador de Producción Agrícola en América")

tab1, tab2 = st.tabs(["Distribución por Año", "Tendencia Temporal"])

with tab1:
    st.subheader("Distribución por año - todos los países")

    year_hist = st.slider(
        "Selecciona el año:",
        int(df_long["Year"].min()),
        int(df_long["Year"].max()),
        value=int(df_long["Year"].max())
    )
    element_hist = st.selectbox(
        "Variable:",
        ["Production","Area harvested"], 
        key="element_hist2"
    )

    # Casillas de verificación para gráficos
    show_hist = st.checkbox("Mostrar Histograma")
    show_scatter = st.checkbox("Mostrar Dispersión")

    if st.button("Generar gráfico por año", key="btn_hist_year"):
        filtered_hist = df_long[
            (df_long["Year"] == year_hist) &
            (df_long["Element"] == element_hist)
        ]

        if filtered_hist.empty:
            st.warning("No hay datos para este año y variable.")
        else:
            title_base = f"{filtered_hist['Description'].iloc[0]} ({element_hist}) en {year_hist} [{filtered_hist['Unit'].iloc[0]}]"

            if not show_hist and not show_scatter:
                st.warning("Selecciona al menos un tipo de gráfico.")
            else:
                if show_hist:
                    fig_hist = px.histogram(
                        filtered_hist,
                        x="Country",
                        y="Value",
                        color="Country",
                        title="Histograma - " + title_base
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)

                if show_scatter:
                    fig_scatter = px.scatter(
                        filtered_hist,
                        x="Country",
                        y="Value",
                        color="Country",
                        size="Value",
                        title="Dispersión - " + title_base
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)


# =====================================
# TAB 2: Tendencia Temporal
# =====================================
with tab2:
    st.subheader("Comparación de tendencia temporal")

    countries_line = st.multiselect("País(es) a comparar:", sorted(df_long["Country"].unique()), default=["Costa Rica"])
    crop_line = st.selectbox("Cultivo:", sorted(df_long["Item"].unique()), key="crop_line")
    element_line = st.selectbox("Variable:", ["Production","Area harvested","Yield"], key="element_line")

    if st.button("Generar tendencia temporal"):
        trend_data = df_long[
            (df_long["Country"].isin(countries_line)) &
            (df_long["Item"]==crop_line) &
            (df_long["Element"]==element_line)
        ]

        if trend_data.empty:
            st.warning("No hay datos para esta combinación.")
        else:
            title = f"{trend_data['Description'].iloc[0]} de {crop_line} [{trend_data['Unit'].iloc[0]}]"
            fig = px.line(trend_data, x="Year", y="Value", color="Country", markers=True, title=title)
            st.plotly_chart(fig, use_container_width=True)
