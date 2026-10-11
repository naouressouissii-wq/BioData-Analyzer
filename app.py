

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="BioData Analyzer",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 BioData Analyzer")
st.write("Analyse éducative des mesures de capteurs biomédicaux.")

st.info(
    "Cette application analyse des données fournies par l'utilisateur. "
    "Elle ne réalise aucun diagnostic médical."
)

# Exemple de données si aucun fichier n'est importé
example_data = pd.DataFrame({
    "Temperature": [22.0, 22.5, 23.1, 24.8, 21.9, 22.3],
    "Humidity": [45, 48, 51, 39, 52, 47],
    "CO2": [420, 450, 480, 1100, 460, 440]
})

uploaded_file = st.file_uploader(
    "Importer un fichier CSV",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
    except Exception as error:
        st.error(f"Impossible de lire le fichier : {error}")
        st.stop()
else:
    st.write("Données de démonstration affichées ci-dessous.")
    data = example_data

if data.empty:
    st.warning("Le fichier ne contient aucune mesure.")
    st.stop()

# Sélection des colonnes numériques
numeric_columns = data.select_dtypes(include="number").columns.tolist()

if not numeric_columns:
    st.error("Le fichier doit contenir au moins une colonne numérique.")
    st.stop()

st.subheader("1. Données")
st.dataframe(data, use_container_width=True)

selected_column = st.selectbox(
    "Choisir le paramètre à analyser",
    numeric_columns
)

values = pd.to_numeric(data[selected_column], errors="coerce").dropna()

if values.empty:
    st.warning("Aucune valeur numérique exploitable.")
    st.stop()

# Indicateurs statistiques
col1, col2, col3, col4 = st.columns(4)

col1.metric("Nombre de mesures", len(values))
col2.metric("Moyenne", f"{values.mean():.2f}")
col3.metric("Minimum", f"{values.min():.2f}")
col4.metric("Maximum", f"{values.max():.2f}")

st.subheader("2. Graphique des mesures")
st.line_chart(values.reset_index(drop=True))

st.subheader("3. Détection de valeurs atypiques")

# Détection statistique simple : moyenne +/- 2 écarts-types
mean_value = values.mean()
std_value = values.std()

if std_value == 0 or pd.isna(std_value):
    anomalies = values.iloc[0:0]
else:
    anomalies = values[
        (values < mean_value - 2 * std_value) |
        (values > mean_value + 2 * std_value)
    ]

if anomalies.empty:
    st.success("Aucune valeur atypique détectée selon cette règle.")
else:
    st.warning(f"{len(anomalies)} valeur(s) atypique(s) détectée(s).")
    st.dataframe(anomalies.rename("Valeur atypique"))

st.caption(
    "La détection statistique est indicative. "
    "Elle ne prouve pas qu'une mesure est dangereuse."
)

# Export du tableau
csv_output = data.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Télécharger les données CSV",
    data=csv_output,
    file_name="mesures_analysees.csv",
    mime="text/csv"
)
