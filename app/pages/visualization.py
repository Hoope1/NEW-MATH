# app/pages/visualization.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from app.db_manager import get_all_teilnehmer, get_tests_by_teilnehmer
from app.utils.helper_functions import sort_dataframe_by_date, format_date

# Cache die Teilnehmerliste, um wiederholte Datenbankabfragen zu vermeiden
@st.cache_data
def load_teilnehmer():
    return get_all_teilnehmer()

# Cache die Testergebnisse für einen Teilnehmer
@st.cache_data
def load_tests(teilnehmer_id):
    df_tests = get_tests_by_teilnehmer(teilnehmer_id)
    if not df_tests.empty:
        df_tests = sort_dataframe_by_date(df_tests, 'test_datum')
    return df_tests

def plot_performance(df_tests, teilnehmer_name):
    """
    Erstellt ein interaktives Diagramm der Gesamt- und Kategorieleistung eines Teilnehmers.
    
    Args:
        df_tests (pandas.DataFrame): DataFrame mit Testergebnissen.
        teilnehmer_name (str): Name des Teilnehmers.
    
    Returns:
        plotly.graph_objects.Figure: Das erstellte Diagramm.
    """
    if df_tests.empty:
        return None

    test_dates = pd.to_datetime(df_tests['test_datum'])
    overall_scores = df_tests['gesamt_prozent']

    # Kategorien
    categories = ['textaufgaben', 'raumvorstellung', 'grundrechenarten', 'zahlenraum', 'gleichungen', 'brueche']
    category_scores = {category: df_tests[f"{category}_erreichte_punkte"] / df_tests[f"{category}_max_punkte"] * 100 for category in categories}

    fig = go.Figure()

    # Gesamtleistung
    fig.add_trace(go.Scatter(
        x=test_dates,
        y=overall_scores,
        mode='lines+markers',
        name='Gesamtleistung',
        line=dict(color='black', width=2)
    ))

    # Kategorien hinzufügen
    colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown']
    for idx, category in enumerate(categories):
        fig.add_trace(go.Scatter(
            x=test_dates,
            y=category_scores[category],
            mode='lines+markers',
            name=category.capitalize(),
            line=dict(dash='dot', color=colors[idx], width=1.5)
        ))

    # Diagramm-Layout
    fig.update_layout(
        title=f"Leistungsentwicklung von {teilnehmer_name}",
        xaxis_title="Datum",
        yaxis_title="Prozentwerte",
        xaxis=dict(type="date"),
        yaxis=dict(range=[0, 100]),
        legend_title="Kategorien",
        template="plotly_white",
        hovermode="x unified"
    )

    return fig

def main():
    st.header("Datenvisualisierung der Testergebnisse")

    # Abrufen der Teilnehmerliste
    df_teilnehmer = load_teilnehmer()
    if df_teilnehmer.empty:
        st.warning("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
        return

    # Auswahl des Teilnehmers
    teilnehmer_namen = df_teilnehmer['name'].tolist()
    selected_name = st.selectbox("Teilnehmer auswählen", teilnehmer_namen)
    teilnehmer_data = df_teilnehmer[df_teilnehmer['name'] == selected_name].iloc[0]
    teilnehmer_id = teilnehmer_data['teilnehmer_id']

    # Abrufen der Testergebnisse
    df_tests = load_tests(teilnehmer_id)

    if df_tests.empty:
        st.info("Keine Testergebnisse für diesen Teilnehmer vorhanden.")
    else:
        # Diagramm erstellen
        fig = plot_performance(df_tests, selected_name)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nicht genügend Daten für die Visualisierung.")

        st.markdown("---")

        # Erweiterte Filteroptionen
        st.subheader("Erweiterte Filteroptionen")
        with st.expander("Filter anwenden"):
            min_date = df_tests['test_datum'].min()
            max_date = df_tests['test_datum'].max()
            start_date = st.date_input("Startdatum", pd.to_datetime(min_date))
            end_date = st.date_input("Enddatum", pd.to_datetime(max_date))

            if start_date > end_date:
                st.error("Das Startdatum darf nicht nach dem Enddatum liegen.")
            else:
                # Filtern der Daten
                mask = (pd.to_datetime(df_tests['test_datum']) >= pd.to_datetime(start_date)) & \
                       (pd.to_datetime(df_tests['test_datum']) <= pd.to_datetime(end_date))
                filtered_df = df_tests[mask]

                if filtered_df.empty:
                    st.warning("Keine Testergebnisse in diesem Zeitraum gefunden.")
                else:
                    fig_filtered = plot_performance(filtered_df, selected_name)
                    if fig_filtered:
                        st.plotly_chart(fig_filtered, use_container_width=True)
                    else:
                        st.info("Nicht genügend Daten für die Visualisierung.")

    st.markdown("---")

    # Allgemeine Hinweise zur Visualisierung
    st.markdown("""
    ### Hinweise zur Visualisierung
    - **Gesamtleistung:** Die schwarze Linie zeigt die Gesamtleistung des Teilnehmers über die Zeit.
    - **Kategorieleistung:** Die farbigen gestrichelten Linien repräsentieren die Leistung in den einzelnen Kategorien:
      - **Textaufgaben**
      - **Raumvorstellung**
      - **Grundrechenarten**
      - **Zahlenraum**
      - **Gleichungen**
      - **Brüche**
    - **Interaktivität:** Bewegen Sie den Mauszeiger über die Datenpunkte, um detaillierte Informationen anzuzeigen.
    - **Filter:** Verwenden Sie die erweiterten Filteroptionen, um die Visualisierung auf einen bestimmten Zeitraum zu beschränken.
    """)
