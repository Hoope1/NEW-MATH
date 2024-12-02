# main.py

import streamlit as st
from app.pages import participants, tests, calculations, visualization, reports, prediction

def main():
    # Setzen der Seitenkonfiguration
    st.set_page_config(
        page_title="Teilnehmer- und Testmanagement",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Titel der Anwendung
    st.title("Teilnehmer- und Testmanagement System")
    
    # Seiten-Navigation in der Sidebar
    st.sidebar.title("Navigation")
    pages = {
        "Teilnehmerverwaltung": participants.main,
        "Testdateneingabe und -verwaltung": tests.main,
        "Automatische Berechnungen und Validierung": calculations.main,
        "Datenvisualisierung": visualization.main,
        "Berichterstellung": reports.main,
        "KI-Prognose": prediction.main,
        # Weitere Seiten können hier hinzugefügt werden
    }
    
    # Auswahl der Seite
    selection = st.sidebar.selectbox("Seite auswählen", list(pages.keys()))
    page_function = pages[selection]
    
    # Aufrufen der ausgewählten Seite
    page_function()

if __name__ == "__main__":
    main()
