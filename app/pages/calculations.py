import streamlit as st
from app.db_manager import get_tests_by_teilnehmer
from app.utils.helper_functions import sort_dataframe_by_date
import pandas as pd

def main():
    """
    Hauptfunktion für automatische Berechnungen und Validierung.
    Bietet Statistiken und Kennzahlen auf Basis der Testdaten.
    """
    st.header("Automatische Berechnungen und Validierung")
    st.markdown("""
        In diesem Bereich können Sie die statistischen Berechnungen und Kennzahlen 
        zu den Testdaten der Teilnehmer einsehen. Wählen Sie einen Teilnehmer aus, 
        um die Ergebnisse anzuzeigen.
    """)

    teilnehmer_data = get_all_teilnehmer()
    
    if teilnehmer_data.empty:
        st.info("Keine Teilnehmerdaten vorhanden. Bitte fügen Sie Teilnehmer hinzu.")
        return

    selected_id = st.selectbox(
        "Wählen Sie einen Teilnehmer aus:",
        teilnehmer_data['teilnehmer_id'],
        format_func=lambda x: teilnehmer_data[teilnehmer_data['teilnehmer_id'] == x]['name'].values[0],
        key="select_participant"
    )

    df_tests = get_tests_by_teilnehmer(selected_id)
    
    if df_tests.empty:
        st.info("Keine Testdaten für diesen Teilnehmer vorhanden.")
        return

    # Sortiere Testdaten
    df_tests_sorted = sort_dataframe_by_date(df_tests, "test_datum")

    # Berechnungen
    st.subheader("Statistische Analysen")

    # Durchschnittliche Prozente
    avg_percent = df_tests_sorted['gesamt_prozent'].mean()
    st.metric(label="Durchschnittliche Testergebnisse (%)", value=f"{avg_percent:.2f}")

    # Maximaler und minimaler Prozentsatz
    max_percent = df_tests_sorted['gesamt_prozent'].max()
    min_percent = df_tests_sorted['gesamt_prozent'].min()
    st.metric(label="Höchstes Testergebnis (%)", value=f"{max_percent:.2f}")
    st.metric(label="Niedrigstes Testergebnis (%)", value=f"{min_percent:.2f}")

    # Durchschnitt pro Kategorie
    categories = [
        "textaufgaben", "raumvorstellung", "grundrechenarten",
        "zahlenraum", "gleichungen", "brueche"
    ]
    st.subheader("Durchschnittliche Ergebnisse pro Kategorie (%)")
    avg_categories = {}
    for category in categories:
        avg_categories[category] = (df_tests_sorted[f"{category}_erreichte_punkte"] /
                                    df_tests_sorted[f"{category}_max_punkte"] * 100).mean()
        st.metric(label=f"{category.capitalize()} (%)", value=f"{avg_categories[category]:.2f}")

    # Gesamtstatistik-Tabelle
    st.subheader("Gesamtstatistik")
    df_stats = df_tests_sorted[['test_datum', 'gesamt_erreichte_punkte', 'gesamt_max_punkte', 'gesamt_prozent']].copy()
    df_stats['test_datum'] = df_stats['test_datum'].apply(lambda x: x.strftime('%d.%m.%Y'))
    st.dataframe(df_stats, use_container_width=True)

    # Graphische Darstellung
    st.subheader("Visualisierung der Testergebnisse")
    st.line_chart(data=df_tests_sorted.set_index("test_datum")["gesamt_prozent"])

if __name__ == "__main__":
    main()
