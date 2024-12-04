import streamlit as st
from app.db_manager import add_test, get_tests_by_teilnehmer, update_test, delete_test, get_all_teilnehmer
from app.utils.helper_functions import validate_points, calculate_total_scores, sort_dataframe_by_date, format_date
import pandas as pd
from datetime import datetime

def main():
    """
    Hauptfunktion für die Verwaltung von Testdaten.
    Diese Funktion bietet Tabs für:
    - Übersicht der Tests
    - Hinzufügen neuer Tests
    - Bearbeiten oder Löschen bestehender Tests
    """

    st.header("Testverwaltung")
    tabs = st.tabs(["Übersicht", "Test hinzufügen", "Test bearbeiten/löschen"])

    # Tab: Übersicht
    with tabs[0]:
        st.subheader("Alle Tests anzeigen")
        teilnehmer = get_all_teilnehmer()

        if teilnehmer.empty:
            st.info("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie Teilnehmer hinzu.")
        else:
            selected_id = st.selectbox(
                "Wählen Sie einen Teilnehmer aus:",
                teilnehmer['teilnehmer_id'],
                format_func=lambda x: teilnehmer[teilnehmer['teilnehmer_id'] == x]['name'].values[0]
            )

            df_tests = get_tests_by_teilnehmer(selected_id)
            if df_tests.empty:
                st.info("Keine Tests für diesen Teilnehmer verfügbar.")
            else:
                df_tests_sorted = sort_dataframe_by_date(df_tests, "test_datum")
                df_tests_sorted['test_datum'] = df_tests_sorted['test_datum'].apply(format_date)
                st.dataframe(df_tests_sorted[['test_id', 'test_datum', 'gesamt_erreichte_punkte', 'gesamt_prozent']])

    # Tab: Test hinzufügen
    with tabs[1]:
        st.subheader("Neuen Test hinzufügen")
        teilnehmer = get_all_teilnehmer()

        if teilnehmer.empty:
            st.info("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie Teilnehmer hinzu.")
        else:
            selected_id = st.selectbox(
                "Teilnehmer auswählen:",
                teilnehmer['teilnehmer_id'],
                format_func=lambda x: teilnehmer[teilnehmer['teilnehmer_id'] == x]['name'].values[0]
            )

            with st.form("add_test_form"):
                test_datum = st.date_input("Testdatum:")
                categories = ["textaufgaben", "raumvorstellung", "grundrechenarten", "zahlenraum", "gleichungen", "brueche"]
                erreichte_punkte = {cat: st.number_input(f"Erreichte Punkte für {cat.capitalize()}:", 0.0, 100.0) for cat in categories}
                maximale_punkte = {cat: st.number_input(f"Maximale Punkte für {cat.capitalize()}:", 0.0, 100.0) for cat in categories}

                submitted = st.form_submit_button("Test hinzufügen")
                if submitted:
                    if not validate_points(erreichte_punkte) or not validate_points(maximale_punkte):
                        st.error("Alle Punkte müssen valide sein.")
                    else:
                        gesamt_erreichte_punkte, gesamt_max_punkte, gesamt_prozent = calculate_total_scores({
                            k: {'erreicht': erreichte_punkte[k], 'max': maximale_punkte[k]} for k in erreichte_punkte
                        })
                        add_test(selected_id, test_datum, **{
                            f"{key}_erreichte_punkte": erreichte_punkte[key],
                            f"{key}_max_punkte": maximale_punkte[key]
                            for key in categories
                        }, gesamt_erreichte_punkte=gesamt_erreichte_punkte, gesamt_max_punkte=gesamt_max_punkte, gesamt_prozent=gesamt_prozent)
                        st.success("Test erfolgreich hinzugefügt.")

    # Tab: Test bearbeiten/löschen
    with tabs[2]:
        st.subheader("Tests bearbeiten oder löschen")
        teilnehmer = get_all_teilnehmer()

        if teilnehmer.empty:
            st.info("Keine Teilnehmer vorhanden.")
        else:
            selected_id = st.selectbox(
                "Teilnehmer auswählen:",
                teilnehmer['teilnehmer_id'],
                format_func=lambda x: teilnehmer[teilnehmer['teilnehmer_id'] == x]['name'].values[0]
            )

            df_tests = get_tests_by_teilnehmer(selected_id)
            if df_tests.empty:
                st.info("Keine Tests verfügbar.")
            else:
                selected_test_id = st.selectbox("Test auswählen:", df_tests['test_id'])
                if st.button("Test löschen"):
                    delete_test(selected_test_id)
                    st.success("Test erfolgreich gelöscht.")

if __name__ == "__main__":
    main()
