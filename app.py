
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="MediStock",
    page_icon="🏥",
    layout="wide"
)

FILE = Path("stock_medical.csv")

COLS = ["Nom", "Categorie", "Quantite", "Seuil minimum"]

def load_stock():
    if FILE.exists():
        try:
            df = pd.read_csv(FILE)
            if all(c in df.columns for c in COLS):
                df["Quantite"] = pd.to_numeric(
                    df["Quantite"], errors="coerce"
                )
                df["Seuil minimum"] = pd.to_numeric(
                    df["Seuil minimum"], errors="coerce"
                )
                df = df.dropna(subset=["Quantite", "Seuil minimum"])
                return df[COLS]
        except (OSError, ValueError, pd.errors.ParserError):
            pass

    return pd.DataFrame([
        ["Gants médicaux", "Consommable", 100, 20],
        ["Masques chirurgicaux", "Consommable", 50, 15],
        ["Thermomètre", "Équipement", 8, 3],
        ["Oxymètre de pouls", "Équipement", 4, 2],
    ], columns=COLS)

if "stock" not in st.session_state:
    st.session_state.stock = load_stock()

def save_stock():
    st.session_state.stock.to_csv(FILE, index=False)

st.title("🏥 MediStock")
st.write("Application de gestion du stock de matériel médical.")
st.caption("Projet éducatif — données de démonstration.")

stock = st.session_state.stock

# Tableau de bord
col1, col2, col3 = st.columns(3)

col1.metric("Articles référencés", len(stock))
col2.metric(
    "Quantité totale",
    int(stock["Quantite"].sum()) if not stock.empty else 0
)

low_stock = stock[
    stock["Quantite"] <= stock["Seuil minimum"]
]
col3.metric("Stocks faibles", len(low_stock))

st.divider()

# Recherche
st.subheader("🔎 Rechercher un article")
search = st.text_input("Nom de l'article")

filtered = stock[
    stock["Nom"].str.contains(search, case=False, na=False)
]

st.dataframe(filtered, use_container_width=True, hide_index=True)

# Alerte stock faible
st.subheader("⚠️ Alertes")
if low_stock.empty:
    st.success("Aucun stock faible.")
else:
    st.warning("Certains articles doivent être réapprovisionnés.")
    st.dataframe(low_stock, use_container_width=True, hide_index=True)

st.divider()

# Ajouter un article
st.subheader("➕ Ajouter un article")

with st.form("add_form"):
    name = st.text_input("Nom de l'article")
    category = st.selectbox(
        "Catégorie",
        ["Consommable", "Équipement", "Instrument", "Autre"]
    )
    quantity = st.number_input("Quantité", min_value=0, step=1)
    threshold = st.number_input(
        "Seuil minimum", min_value=0, step=1
    )

    submitted = st.form_submit_button("Ajouter")

    if submitted:
        if not name.strip():
            st.error("Veuillez saisir le nom de l'article.")
        elif stock["Nom"].str.casefold().eq(name.strip().casefold()).any():
            st.error("Cet article existe déjà.")
        else:
            new_row = pd.DataFrame([{
                "Nom": name.strip(),
                "Categorie": category,
                "Quantite": quantity,
                "Seuil minimum": threshold
            }])

            st.session_state.stock = pd.concat(
                [stock, new_row], ignore_index=True
            )
            save_stock()
            st.success("Article ajouté et stock enregistré.")
            st.rerun()

# Modifier les quantités
st.subheader("✏️ Modifier le stock")

if not stock.empty:
    selected = st.selectbox("Choisir un article", stock["Nom"].tolist())
    current = stock[stock["Nom"] == selected].iloc[0]

    with st.form("edit_form"):
        new_quantity = st.number_input(
            "Nouvelle quantité",
            min_value=0,
            value=int(current["Quantite"]),
            step=1
        )

        updated = st.form_submit_button("Enregistrer la quantité")

        if updated:
            st.session_state.stock.loc[
                st.session_state.stock["Nom"] == selected,
                "Quantite"
            ] = new_quantity

            save_stock()
            st.success("Quantité mise à jour.")
            st.rerun()

# Supprimer un article
st.subheader("🗑️ Supprimer un article")

if not stock.empty:
    to_delete = st.selectbox(
        "Article à supprimer",
        stock["Nom"].tolist(),
        key="delete_select"
    )

    if st.button("Supprimer l'article"):
        st.session_state.stock = stock[
            stock["Nom"] != to_delete
        ].reset_index(drop=True)

        save_stock()
        st.success("Article supprimé.")
        st.rerun()

st.divider()

# Export CSV
st.subheader("📥 Exporter le stock")

st.download_button(
    "Télécharger le stock au format CSV",
    data=st.session_state.stock.to_csv(index=False).encode("utf-8"),
    file_name="stock_medical.csv",
    mime="text/csv"
)
