# app/pages/tests.py

import streamlit as st
from app.db_manager import add_test, get_tests_by_teilnehmer, update_test, delete_test, get_all_teilnehmer
from app.utils.helper_functions import validate_points, calculate_total_scores, sort_dataframe_by_date, format_date
import pandas as pd


def main():
    """
    Hauptfunktion für die Testdateneingabe und -verwaltung:
    Ermöglicht das Hinzufügen, Bearbeiten und Löschen von Tests sowie die Anzeige aller Testergebnisse.
    """
    st.header("Testdateneingabe und -verwaltung")

    # Tab-Layout für unterschiedliche Funktionen
    tabs = st.tabs(["Übersicht", "Test hinzufügen", "Test bearbeiten/löschen"])

    # Tab: Übersicht
    with tabs[0]:
        st.subheader("Alle Tests")
        teilnehmer = get_all_teilnehmer()
        if teilnehmer.empty:
            st.info("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
        else:
            teilnehmer_name = st.selectbox("Teilnehmer auswählen", teilnehmer['name'].tolist())
            teilnehmer_data = teilnehmer[teilnehmer['name'] == teilnehmer_name].iloc[0]
            teilnehmer_id = teilnehmer_data['teilnehmer_id']
            df_tests = get_tests_by_teilnehmer(teilnehmer_id)

            if df_tests.empty:
                st.info("Keine Testergebnisse für diesen Teilnehmer vorhanden.")
            else:
                df_tests = sort_dataframe_by_date(df_tests, 'test_datum')
                df_display = df_tests.copy()
                df_display['test_datum'] = df_display['test_datum'].apply(format_date)
                st.dataframe(
                    df_display[['test_id', 'test_datum', 'gesamt_erreichte_punkte', 'gesamt_max_punkte', 'gesamt_prozent']].set_index('test_id'),
                    use_container_width=True
                )

    # Tab: Test hinzufügen
    with tabs[1]:
        st.subheader("Neuen Test hinzufügen")
        teilnehmer = get_all_teilnehmer()
        if teilnehmer.empty:
            st.info("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
        else:
            teilnehmer_name = st.selectbox("Teilnehmer auswählen", teilnehmer['name'].tolist())
            teilnehmer_data = teilnehmer[teilnehmer['name'] == teilnehmer_name].iloc[0]
            teilnehmer_id = teilnehmer_data['teilnehmer_id']

            with st.form("add_test_form"):
                test_datum = st.date_input("Testdatum")
                punktesystem = {
                    "Textaufgaben": ["textaufgaben_erreichte_punkte", "textaufgaben_max_punkte"],
                    "Raumvorstellung": ["raumvorstellung_erreichte_punkte", "raumvorstellung_max_punkte"],
                    "Grundrechenarten": ["grundrechenarten_erreichte_punkte", "grundrechenarten_max_punkte"],
                    "Zahlenraum": ["zahlenraum_erreichte_punkte", "zahlenraum_max_punkte"],
                    "Gleichungen": ["gleichungen_erreichte_punkte", "gleichungen_max_punkte"],
                    "Brüche": ["brueche_erreichte_punkte", "brueche_max_punkte"],
                }

                inputs = {}
                for category, fields in punktesystem.items():
                    col1, col2 = st.columns(2)
                    with col1:
                        inputs[fields[0]] = st.number_input(f"Erreichte Punkte - {category}", min_value=0.0, max_value=100.0, step=0.1)
                    with col2:
                        inputs[fields[1]] = st.number_input(f"Maximale Punkte - {category}", min_value=0.0, max_value=100.0, step=0.1)

                submitted = st.form_submit_button("Test hinzufügen")
                if submitted:
                    if not validate_points({key: inputs[key] for key in punktesystem}):
                        st.error("Bitte geben Sie gültige Punkte ein.")
                    else:
                        gesamt_erreichte_punkte, gesamt_max_punkte, gesamt_prozent = calculate_total_scores({
                            key: {"erreicht": inputs[fields[0]], "max": inputs[fields[1]]}
                            for key, fields in punktesystem.items()
                        })

                        try:
                            add_test(
                                teilnehmer_id=teilnehmer_id,
                                test_datum=test_datum.strftime('%Y-%m-%d'),
                                gesamt_erreichte_punkte=gesamt_erreichte_punkte,
                                gesamt_max_punkte=gesamt_max_punkte,
                                gesamt_prozent=gesamt_prozent,
                                **inputs
                            )
                            st.success("Test erfolgreich hinzugefügt.")
                        except Exception as e:
                            st.error(f"Fehler beim Hinzufügen des Tests: {e}")

    # Tab: Test bearbeiten/löschen
    with tabs[2]:
        st.subheader("Test bearbeiten oder löschen")
        teilnehmer = get_all_teilnehmer()
        if teilnehmer.empty:
            st.info("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
        else:
            teilnehmer_name = st.selectbox("Teilnehmer auswählen", teilnehmer['name'].tolist())
            teilnehmer_data = teilnehmer[teilnehmer['name'] == teilnehmer_name].iloc[0]
            teilnehmer_id = teilnehmer_data['teilnehmer_id']
            df_tests = get_tests_by_teilnehmer(teilnehmer_id)

            if df_tests.empty:
                st.info("Keine Testergebnisse für diesen Teilnehmer vorhanden.")
            else:
                df_tests = sort_dataframe_by_date(df_tests, 'test_datum')
                test_id = st.selectbox("Test auswählen", df_tests['test_id'].tolist())
                selected_test = df_tests[df_tests['test_id'] == test_id].iloc[0]

                with st.expander("Test bearbeiten"):
                    with st.form("edit_test_form"):
                        test_datum = st.date_input("Testdatum", value=pd.to_datetime(selected_test['test_datum']))
                        punktesystem = {
                            "Textaufgaben": ["textaufgaben_erreichte_punkte", "textaufgaben_max_punkte"],
                            "Raumvorstellung": ["raumvorstellung_erreichte_punkte", "raumvorstellung_max_punkte"],
                            "Grundrechenarten": ["grundrechenarten_erreichte_punkte", "grundrechenarten_max_punkte"],
                            "Zahlenraum": ["zahlenraum_erreichte_punkte", "zahlenraum_max_punkte"],
                            "Gleichungen": ["gleichungen_erreichte_punkte", "gleichungen_max_punkte"],
                            "Brüche": ["brueche_erreichte_punkte", "brueche_max_punkte"],
                        }

                        inputs = {}
                        for category, fields in punktesystem.items():
                            col1, col2 = st.columns(2)
                            with col1:
                                inputs[fields[0]] = st.number_input(
                                    f"Erreichte Punkte - {category}",
                                    min_value=0.0,
                                    max_value=100.0,
                                    value=selected_test[fields[0]],
                                    step=0.1
                                )
                            with col2:
                                inputs[fields[1]] = st.number_input(
                                    f"Maximale Punkte - {category}",
                                    min_value=0.0,
                                    max_value=100.0,
                                    value=selected_test[fields[1]],
                                    step=0.1
                                )

                        submitted = st.form_submit_button("Test aktualisieren")
                        if submitted:
                            gesamt_erreichte_punkte, gesamt_max_punkte, gesamt_prozent = calculate_total_scores({
                                key: {"erreicht": inputs[fields[0]], "max": inputs[fields[1]]}
                                for key, fields in punktesystem.items()
                            })

                            try:
                                update_test(
                                    test_id=test_id,
                                    test_datum=test_datum.strftime('%Y-%m-%d'),
                                    gesamt_erreichte_punkte=gesamt_erreichte_punkte,
                                    gesamt_max_punkte=gesamt_max_punkte,
                                    gesamt_prozent=gesamt_prozent,
                                    **inputs
                                )
                                st.success("Test erfolgreich aktualisiert.")
                            except Exception as e:
                                st.error(f"Fehler beim Aktualisieren des Tests: {e}")

                with st.expander("Test löschen"):
                    if st.button("Test löschen"):
                        try:
                            delete_test(test_id)
                            st.success("Test erfolgreich gelöscht.")
                        except Exception as e:
                            st.error(f"Fehler beim Löschen des Tests: {e}")


if __name__ == "__main__":
    main()
