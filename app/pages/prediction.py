import streamlit as st
from app.db_manager import get_tests_by_teilnehmer, get_all_teilnehmer
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    """
    Hauptfunktion zur KI-gestützten Prognose.
    Bietet Funktionen zur Visualisierung und Vorhersage der Testergebnisse eines Teilnehmers.
    """
    st.header("KI-Prognose der Testergebnisse")
    st.markdown("""
        In diesem Bereich können Sie die prognostizierte Entwicklung der Testergebnisse eines Teilnehmers 
        basierend auf vorhandenen Daten einsehen. Drücken Sie den LEARN-Button, um die KI zu trainieren.
    """)

    # Teilnehmerauswahl
    teilnehmer_data = get_all_teilnehmer()
    
    if teilnehmer_data.empty:
        st.info("Keine Teilnehmerdaten vorhanden. Bitte fügen Sie Teilnehmer hinzu.")
        return

    selected_id = st.selectbox(
        "Wählen Sie einen Teilnehmer aus:",
        teilnehmer_data['teilnehmer_id'],
        format_func=lambda x: teilnehmer_data[teilnehmer_data['teilnehmer_id'] == x]['name'].values[0],
        key="select_prediction_participant"
    )

    df_tests = get_tests_by_teilnehmer(selected_id)

    if df_tests.empty:
        st.info("Keine Testdaten für diesen Teilnehmer vorhanden.")
        return

    # Datenvorbereitung
    df_tests_sorted = df_tests.sort_values(by="test_datum")
    df_tests_sorted['days_since_start'] = (pd.to_datetime(df_tests_sorted['test_datum']) - pd.to_datetime(df_tests_sorted['test_datum']).min()).dt.days
    x = df_tests_sorted['days_since_start'].values.reshape(-1, 1)
    y = df_tests_sorted['gesamt_prozent'].values

    # Visualisierung der bisherigen Testergebnisse
    st.subheader("Bisherige Testergebnisse")
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, color='blue', label='Tatsächliche Ergebnisse')
    plt.xlabel("Tage seit erstem Test")
    plt.ylabel("Gesamtprozent (%)")
    plt.title("Entwicklung der Testergebnisse")
    st.pyplot(plt)

    # LEARN-Button
    if st.button("LEARN - Modell trainieren"):
        model = train_model(x, y)
        st.success("Das Modell wurde erfolgreich trainiert.")

        # Prognose für die nächsten 30 Tage
        st.subheader("Prognose für die nächsten 30 Tage")
        future_x = np.arange(x.max() + 1, x.max() + 31).reshape(-1, 1)
        future_y = model.predict(future_x)

        # Darstellung der Prognose
        plt.figure(figsize=(10, 6))
        plt.scatter(x, y, color='blue', label='Tatsächliche Ergebnisse')
        plt.plot(future_x, future_y, color='red', linestyle='--', label='Prognose')
        plt.xlabel("Tage seit erstem Test")
        plt.ylabel("Gesamtprozent (%)")
        plt.title("Prognostizierte Entwicklung der Testergebnisse")
        plt.legend()
        st.pyplot(plt)

def train_model(x, y):
    """
    Trainiert ein einfaches lineares Regressionsmodell basierend auf den gegebenen Daten.
    Args:
        x (numpy.ndarray): Eingabedaten (z. B. Tage seit erstem Test).
        y (numpy.ndarray): Zielwerte (z. B. Testergebnisse in Prozent).
    Returns:
        LinearRegression: Das trainierte Modell.
    """
    model = LinearRegression()
    model.fit(x, y)
    return model

if __name__ == "__main__":
    main()
