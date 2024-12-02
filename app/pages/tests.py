# app/pages/tests.py

import streamlit as st
import pandas as pd
from datetime import datetime
from app.db_manager import (
    add_test,
    get_tests_by_teilnehmer,
    update_test,
    delete_test,
    get_all_teilnehmer
)
from app.utils.helper_functions import validate_points, calculate_total_scores, format_date, sort_dataframe_by_date


def main():
    """
    Hauptfunktion zur Verwaltung von Tests: 
    Ermöglicht das Anzeigen, Hinzufügen, Bearbeiten und Löschen von Tests.
    """
    st.header("Testdateneingabe und -verwaltung")

    # Tabs für verschiedene Funktionen
    tabs = st.tabs(["Übersicht", "Test hinzufügen", "Test bearbeiten/löschen"])

    with tabs[0]:
        st.subheader("Alle Tests")
        teilnehmer_df = get_all_teilnehmer()
        if teilnehmer_df.empty:
            st.info("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
            return

        # Auswahl des Teilnehmers
        teilnehmer_name = st.selectbox(
            "Teilnehmer auswählen",
            teilnehmer_df['name'].tolist()
        )
        teilnehmer_id = teilnehmer_df[teilnehmer_df['name'] == teilnehmer_name]['teilnehmer_id'].iloc[0]
        tests_df = get_tests_by_teilnehmer(teilnehmer_id)

        if tests_df.empty:
            st.info("Keine Testergebnisse für diesen Teilnehmer vorhanden.")
        else:
            tests_df['test_datum'] = tests_df['test_datum'].apply(format_date)
            st.dataframe(
                tests_df[[
                    'test_id', 'test_datum', 'gesamt_erreichte_punkte',
                    'gesamt_max_punkte', 'gesamt_prozent'
                ]].set_index('test_id'),
                use_container_width=True
            )

    with tabs[1]:
        st.subheader("Neuen Test hinzufügen")
        if teilnehmer_df.empty:
            st.info("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
            return

        teilnehmer_name = st.selectbox(
            "Teilnehmer auswählen",
            teilnehmer_df['name'].tolist()
        )
        teilnehmer_id = teilnehmer_df[teilnehmer_df['name'] == teilnehmer_name]['teilnehmer_id'].iloc[0]

        with st.form("add_test_form"):
            test_datum = st.date_input("Testdatum", value=datetime.now().date())

            # Punkte für jede Kategorie
            categories = {
                "textaufgaben": "Textaufgaben",
                "raumvorstellung": "Raumvorstellung",
                "grundrechenarten": "Grundrechenarten",
                "zahlenraum": "Zahlenraum",
                "gleichungen": "Gleichungen",
                "brueche": "Brüche"
            }
            erreichte_punkte = {}
            maximale_punkte = {}

            for key, label in categories.items():
                erreichte_punkte[key] = st.number_input(f"Erreichte Punkte - {label}", min_value=0.0, max_value=100.0, step=0.1)
                maximale_punkte[key] = st.number_input(f"Maximale Punkte - {label}", min_value=0.0, max_value=100.0, step=0.1)

            submitted = st.form_submit_button("Test hinzufügen")

            if submitted:
                # Validierung der Eingabedaten
                if not validate_points(erreichte_punkte):
                    st.error("Bitte geben Sie gültige Werte für erreichte Punkte ein.")
                elif not validate_points(maximale_punkte):
                    st.error("Bitte geben Sie gültige Werte für maximale Punkte ein.")
                elif sum(maximale_punkte.values()) != 100:
                    st.error("Die Summe der maximalen Punkte muss genau 100 betragen.")
                else:
                    # Berechnung der Gesamtergebnisse
                    gesamt_erreichte, gesamt_max, gesamt_prozent = calculate_total_scores(
                        {key: {"erreicht": erreichte_punkte[key], "max": maximale_punkte[key]} for key in categories}
                    )
                    try:
                        add_test(
                            teilnehmer_id=teilnehmer_id,
                            test_datum=test_datum.strftime('%Y-%m-%d'),
                            **{f"{key}_erreichte_punkte": erreichte_punkte[key] for key in categories},
                            **{f"{key}_max_punkte": maximale_punkte[key] for key in categories},
                            gesamt_erreichte_punkte=gesamt_erreichte,
                            gesamt_max_punkte=gesamt_max,
                            gesamt_prozent=gesamt_prozent
                        )
                        st.success("Test erfolgreich hinzugefügt.")
                    except Exception as e:
                        st.error(f"Fehler beim Hinzufügen des Tests: {e}")

    with tabs[2]:
        st.subheader("Test bearbeiten oder löschen")
        if teilnehmer_df.empty:
            st.info("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
            return

        teilnehmer_name = st.selectbox(
            "Teilnehmer auswählen",
            teilnehmer_df['name'].tolist()
        )
        teilnehmer_id = teilnehmer_df[teilnehmer_df['name'] == teilnehmer_name]['teilnehmer_id'].iloc[0]
        tests_df = get_tests_by_teilnehmer(teilnehmer_id)

        if tests_df.empty:
            st.info("Keine Testergebnisse für diesen Teilnehmer vorhanden.")
            return

        test_id = st.selectbox(
            "Test auswählen",
            tests_df['test_id'].tolist(),
            format_func=lambda x: f"Test-ID: {x}, Datum: {tests_df[tests_df['test_id'] == x]['test_datum'].iloc[0]}"
        )
        selected_test = tests_df[tests_df['test_id'] == test_id].iloc[0]

        with st.expander("Testdaten bearbeiten"):
            with st.form("edit_test_form"):
                test_datum = st.date_input("Testdatum", value=datetime.strptime(selected_test['test_datum'], '%Y-%m-%d').date())

                # Punkte für jede Kategorie
                erreichte_punkte = {}
                maximale_punkte = {}

                for key, label in categories.items():
                    erreichte_punkte[key] = st.number_input(
                        f"Erreichte Punkte - {label}",
                        value=selected_test[f"{key}_erreichte_punkte"],
                        min_value=0.0, max_value=100.0, step=0.1
                    )
                    maximale_punkte[key] = st.number_input(
                        f"Maximale Punkte - {label}",
                        value=selected_test[f"{key}_max_punkte"],
                        min_value=0.0, max_value=100.0, step=0.1
                    )

                submitted = st.form_submit_button("Test aktualisieren")

                if submitted:
                    if not validate_points(erreichte_punkte):
                        st.error("Bitte geben Sie gültige Werte für erreichte Punkte ein.")
                    elif not validate_points(maximale_punkte):
                        st.error("Bitte geben Sie gültige Werte für maximale Punkte ein.")
                    elif sum(maximale_punkte.values()) != 100:
                        st.error("Die Summe der maximalen Punkte muss genau 100 betragen.")
                    else:
                        gesamt_erreichte, gesamt_max, gesamt_prozent = calculate_total_scores(
                            {key: {"erreicht": erreichte_punkte[key], "max": maximale_punkte[key]} for key in categories}
                        )
                        try:
                            update_test(
                                test_id=test_id,
                                test_datum=test_datum.strftime('%Y-%m-%d'),
                                **{f"{key}_erreichte_punkte": erreichte_punkte[key] for key in categories},
                                **{f"{key}_max_punkte": maximale_punkte[key] for key in categories},
                                gesamt_erreichte_punkte=gesamt_erreichte,
                                gesamt_max_punkte=gesamt_max,
                                gesamt_prozent=gesamt_prozent
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
