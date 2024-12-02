# app/pages/prediction.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from prophet import Prophet
from app.db_manager import get_all_teilnehmer, get_tests_by_teilnehmer
from app.utils.helper_functions import sort_dataframe_by_date, format_date
import plotly.graph_objects as go

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

def create_forecast(df, periods=30):
    """
    Erstellt eine Prognose mit dem Prophet-Modell.
    
    Args:
        df (pandas.DataFrame): DataFrame mit den historischen Daten (ds, y).
        periods (int): Anzahl der zukünftigen Tage für die Prognose.
    
    Returns:
        pandas.DataFrame: DataFrame mit den Prognoseergebnissen.
    """
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast

def plot_forecast(df_tests, forecast, teilnehmer_name):
    """
    Erstellt ein interaktives Diagramm mit historischen und prognostizierten Daten.
    
    Args:
        df_tests (pandas.DataFrame): Historische Testergebnisse.
        forecast (pandas.DataFrame): Prognoseergebnisse von Prophet.
        teilnehmer_name (str): Name des Teilnehmers.
    
    Returns:
        plotly.graph_objects.Figure: Das erstellte Diagramm.
    """
    fig = go.Figure()

    # Historische Daten
    fig.add_trace(go.Scatter(
        x=df_tests['test_datum'],
        y=df_tests['gesamt_prozent'],
        mode='lines+markers',
        name='Historische Gesamtleistung',
        line=dict(color='black', width=2)
    ))

    # Prognose
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat'],
        mode='lines',
        name='Prognose Gesamtleistung',
        line=dict(dash='dash', color='blue', width=2)
    ))

    # Unsicherheitsbereiche
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_upper'],
        mode='lines',
        name='Prognose (Obergrenze)',
        line=dict(dash='dot', color='green'),
        showlegend=True
    ))
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_lower'],
        mode='lines',
        name='Prognose (Untergrenze)',
        line=dict(dash='dot', color='red'),
        fill='tonexty',
        fillcolor='rgba(255, 0, 0, 0.1)',
        showlegend=True
    ))

    # Diagramm-Layout
    fig.update_layout(
        title=f"Prognose der Gesamtleistung von {teilnehmer_name}",
        xaxis_title="Datum",
        yaxis_title="Prozentwerte",
        xaxis=dict(type="date"),
        yaxis=dict(range=[0, 100]),
        legend_title="Leistung",
        template="plotly_white",
        hovermode="x unified"
    )

    return fig

def main():
    st.title("KI-Prognose der Testergebnisse")

    st.markdown("""
    ### Prognose der zukünftigen Gesamtleistung
    Wählen Sie einen Teilnehmer aus, um eine 30-Tage-Prognose der Gesamtleistung zu sehen. Die Prognose basiert auf den historischen Testergebnissen und zeigt die erwarteten Werte mit Unsicherheitsbereichen.
    """)

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
        return

    # Sortieren der Testergebnisse nach Datum
    df_tests = sort_dataframe_by_date(df_tests, 'test_datum')

    # Überprüfen, ob genügend Datenpunkte vorhanden sind
    if len(df_tests) < 2:
        st.warning("Nicht genügend Datenpunkte für eine zuverlässige Prognose. Fügen Sie mindestens zwei Testergebnisse hinzu.")
        return

    # Daten für Prophet vorbereiten
    df_prophet = df_tests[['test_datum', 'gesamt_prozent']].rename(columns={'test_datum': 'ds', 'gesamt_prozent': 'y'})
    df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])

    # Prognose erstellen
    with st.spinner("Erstelle Prognose..."):
        forecast = create_forecast(df_prophet, periods=30)

    # Visualisierung der Prognose
    fig = plot_forecast(df_tests, forecast, selected_name)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Download der Prognoseergebnisse als CSV
    st.subheader("Prognoseergebnisse herunterladen")
    forecast_display = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    forecast_display['ds'] = forecast_display['ds'].dt.strftime('%Y-%m-%d')
    forecast_display = forecast_display.rename(columns={
        'ds': 'Datum',
        'yhat': 'Prognose',
        'yhat_lower': 'Prognose Untergrenze',
        'yhat_upper': 'Prognose Obergrenze'
    })
    st.download_button(
        label="Prognose als CSV herunterladen",
        data=forecast_display.to_csv(index=False).encode('utf-8'),
        file_name=f"{selected_name}_Prognose.csv",
        mime="text/csv"
    )

    st.markdown("---")

    # Hinweise zur Prognose
    st.markdown("""
    ### Hinweise zur Prognose
    - **Historische Gesamtleistung:** Die schwarze Linie zeigt die bisherige Gesamtleistung des Teilnehmers.
    - **Prognose:** Die blaue gestrichelte Linie repräsentiert die prognostizierte Gesamtleistung für die nächsten 30 Tage.
    - **Unsicherheitsbereiche:** Die grünen und roten gestrichelten Linien stellen die obere und untere Grenze der Prognose dar.
    - **Interaktivität:** Bewegen Sie den Mauszeiger über die Datenpunkte, um detaillierte Informationen anzuzeigen.
    """)

    st.markdown("---")

    # Anpassungen und Feedback
    st.markdown("""
    ### Feedback und Anpassungen
    Wenn Sie Verbesserungen oder Anpassungen an der Prognose wünschen, kontaktieren Sie bitte den Administrator.
    """)

if __name__ == "__main__":
    main()
