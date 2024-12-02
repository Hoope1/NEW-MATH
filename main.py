# main.py

import streamlit as st
from app.pages.participants import main as participants_main
from app.pages.tests import main as tests_main
from app.pages.calculations import main as calculations_main
from app.pages.visualization import main as visualization_main
from app.pages.reports import main as reports_main
from app.pages.prediction import main as prediction_main


def main():
    """
    Hauptfunktion zur Steuerung der Streamlit-Anwendung.
    Konfiguriert die Anwendung, ermöglicht die Seitennavigation und ruft die jeweiligen
    Funktionsmodule für die ausgewählten Seiten auf.
    """
    # Konfiguration der Streamlit-Seitenparameter
    st.set_page_config(
        page_title="Teilnehmer- und Testmanagement",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Titel und Begrüßungstext der Anwendung
    st.title("Teilnehmer- und Testmanagement System")
    st.markdown("""
    Willkommen im Teilnehmer- und Testmanagement System! Nutzen Sie die Navigation
    in der Sidebar, um verschiedene Funktionen wie Teilnehmerverwaltung, Testergebnisse,
    Berechnungen, Datenvisualisierungen, Berichte und KI-gestützte Prognosen zu erkunden.
    """)

    # Sidebar für die Navigation zwischen verschiedenen Seiten
    st.sidebar.title("Navigation")
    st.sidebar.info("Wählen Sie eine Seite, um fortzufahren.")

    # Definition der verfügbaren Seiten und Zuordnung ihrer Hauptfunktionen
    pages = {
        "Teilnehmerverwaltung": participants_main,
        "Testdateneingabe und -verwaltung": tests_main,
        "Automatische Berechnungen und Validierung": calculations_main,
        "Datenvisualisierung": visualization_main,
        "Berichterstellung": reports_main,
        "KI-Prognose": prediction_main
    }

    # Auswahl einer Seite durch den Benutzer
    selection = st.sidebar.selectbox(
        "Seite auswählen",
        options=list(pages.keys()),
        index=0  # Standardmäßig ist die erste Seite ausgewählt
    )

    # Aufruf der Hauptfunktion der ausgewählten Seite
    if selection:
        page_function = pages[selection]
        try:
            page_function()
        except Exception as e:
            st.error(f"Es ist ein Fehler auf der Seite '{selection}' aufgetreten: {e}")


# Ausführung des Hauptprogramms
if __name__ == "__main__":
    main()
