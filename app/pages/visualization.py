import streamlit as st
from app.db_manager import get_tests_by_teilnehmer, get_all_teilnehmer
import pandas as pd
import matplotlib.pyplot as plt

def main():
    """
    Hauptfunktion zur Visualisierung der Testergebnisse.
    Bietet interaktive Diagramme zur Analyse der Fortschritte der Teilnehmer.
    """
    st.header("Visualisierung der Testergebnisse")
    st.markdown("""
        In diesem Bereich können Sie die Fortschritte der Teilnehmer visualisieren. 
        Wählen Sie einen Teilnehmer aus, um detaillierte Diagramme zu sehen.
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
        key="select_visualization_participant"
    )

    df_tests = get_tests_by_teilnehmer(selected_id)

    if df_tests.empty:
        st.info("Keine Testdaten für diesen Teilnehmer vorhanden.")
        return

    # Datenvorbereitung
    df_tests_sorted = df_tests.sort_values(by="test_datum")
    df_tests_sorted['test_datum'] = pd.to_datetime(df_tests_sorted['test_datum'])
    df_tests_sorted.set_index('test_datum', inplace=True)

    # Diagrammoptionen
    st.subheader("Diagrammoptionen")
    show_categories = st.checkbox("Einzelne Kategorien anzeigen", value=False)

    # Visualisierung: Gesamtprozentwerte
    st.subheader("Fortschritt der Gesamtprozentwerte")
    plt.figure(figsize=(10, 6))
    plt.plot(df_tests_sorted.index, df_tests_sorted['gesamt_prozent'], marker='o', label='Gesamtprozent')
    plt.xlabel("Datum")
    plt.ylabel("Prozent (%)")
    plt.title("Gesamtprozentwerte über die Zeit")
    plt.legend()
    st.pyplot(plt)

    # Visualisierung: Kategorien (optional)
    if show_categories:
        st.subheader("Fortschritt in einzelnen Kategorien")
        categories = [
            "textaufgaben", "raumvorstellung", "grundrechenarten",
            "zahlenraum", "gleichungen", "brueche"
        ]
        plt.figure(figsize=(10, 6))
        for category in categories:
            category_percent = (df_tests_sorted[f"{category}_erreichte_punkte"] /
                                df_tests_sorted[f"{category}_max_punkte"] * 100)
            plt.plot(df_tests_sorted.index, category_percent, marker='o', label=category.capitalize())
        plt.xlabel("Datum")
        plt.ylabel("Prozent (%)")
        plt.title("Fortschritt in den Kategorien")
        plt.legend()
        st.pyplot(plt)

if __name__ == "__main__":
    main()
