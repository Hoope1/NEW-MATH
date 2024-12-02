# app/pages/tests.py

import streamlit as st
import pandas as pd
from datetime import datetime
from app.db_manager import (
    add_test,
    get_tests_by_teilnehmer,
    get_all_teilnehmer,
    update_test,
    delete_test
)
from app.utils.helper_functions import (
    validate_points,
    calculate_total_scores,
    sort_dataframe_by_date,
    format_date
)

def main():
    st.title("Testdateneingabe und -verwaltung")

    # Menüauswahl
    menu = ["Neues Testergebnis hinzufügen", "Testergebnisse anzeigen"]
    choice = st.sidebar.selectbox("Aktion auswählen", menu)

    if choice == "Neues Testergebnis hinzufügen":
        st.subheader("Neues Testergebnis hinzufügen")

        # Abrufen der Teilnehmerliste
        df_teilnehmer = get_all_teilnehmer()
        if df_teilnehmer.empty:
            st.warning("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
            return

        # Auswahl des Teilnehmers
        teilnehmer_namen = df_teilnehmer['name'].tolist()
        selected_name = st.selectbox("Teilnehmer auswählen", teilnehmer_namen)
        teilnehmer_data = df_teilnehmer[df_teilnehmer['name'] == selected_name].iloc[0]
        teilnehmer_id = teilnehmer_data['teilnehmer_id']

        # Eingabeformular für Testergebnisse
        with st.form(key='add_test_form'):
            test_datum = st.date_input("Testdatum", datetime.today())

            st.markdown("#### Punkteingabe pro Kategorie")
            textaufgaben_erreicht = st.number_input("Erreichte Punkte - Textaufgaben", min_value=0.0, max_value=100.0, value=0.0)
            textaufgaben_max = st.number_input("Maximale Punkte - Textaufgaben", min_value=0.0, max_value=100.0, value=0.0)

            raumvorstellung_erreicht = st.number_input("Erreichte Punkte - Raumvorstellung", min_value=0.0, max_value=100.0, value=0.0)
            raumvorstellung_max = st.number_input("Maximale Punkte - Raumvorstellung", min_value=0.0, max_value=100.0, value=0.0)

            grundrechenarten_erreicht = st.number_input("Erreichte Punkte - Grundrechenarten", min_value=0.0, max_value=100.0, value=0.0)
            grundrechenarten_max = st.number_input("Maximale Punkte - Grundrechenarten", min_value=0.0, max_value=100.0, value=0.0)

            zahlenraum_erreicht = st.number_input("Erreichte Punkte - Zahlenraum", min_value=0.0, max_value=100.0, value=0.0)
            zahlenraum_max = st.number_input("Maximale Punkte - Zahlenraum", min_value=0.0, max_value=100.0, value=0.0)

            gleichungen_erreicht = st.number_input("Erreichte Punkte - Gleichungen", min_value=0.0, max_value=100.0, value=0.0)
            gleichungen_max = st.number_input("Maximale Punkte - Gleichungen", min_value=0.0, max_value=100.0, value=0.0)

            brueche_erreicht = st.number_input("Erreichte Punkte - Brüche", min_value=0.0, max_value=100.0, value=0.0)
            brueche_max = st.number_input("Maximale Punkte - Brüche", min_value=0.0, max_value=100.0, value=0.0)

            submit_button = st.form_submit_button(label="Testergebnis hinzufügen")

        if submit_button:
            # Punkte validieren
            points_dict = {
                'textaufgaben': {'erreicht': textaufgaben_erreicht, 'max': textaufgaben_max},
                'raumvorstellung': {'erreicht': raumvorstellung_erreicht, 'max': raumvorstellung_max},
                'grundrechenarten': {'erreicht': grundrechenarten_erreicht, 'max': grundrechenarten_max},
                'zahlenraum': {'erreicht': zahlenraum_erreicht, 'max': zahlenraum_max},
                'gleichungen': {'erreicht': gleichungen_erreicht, 'max': gleichungen_max},
                'brueche': {'erreicht': brueche_erreicht, 'max': brueche_max}
            }

            if not validate_points({k: v['erreicht'] for k, v in points_dict.items()}):
                st.error("Bitte geben Sie gültige erreichte Punkte ein.")
            elif not validate_points({k: v['max'] for k, v in points_dict.items()}):
                st.error("Bitte geben Sie gültige maximale Punkte ein.")
            else:
                # Gesamtsumme der maximalen Punkte prüfen
                gesamt_max_punkte = sum([v['max'] for v in points_dict.values()])
                if gesamt_max_punkte != 100:
                    st.error("Die Gesamtsumme der maximalen Punkte muss genau 100 betragen.")
                else:
                    # Gesamtpunkte und Gesamtprozent berechnen
                    gesamt_erreichte_punkte, _, gesamt_prozent = calculate_total_scores(points_dict)

                    # Testergebnis speichern
                    add_test(
                        teilnehmer_id=teilnehmer_id,
                        test_datum=test_datum.strftime("%Y-%m-%d"),
                        textaufgaben_erreichte_punkte=textaufgaben_erreicht,
                        textaufgaben_max_punkte=textaufgaben_max,
                        raumvorstellung_erreichte_punkte=raumvorstellung_erreicht,
                        raumvorstellung_max_punkte=raumvorstellung_max,
                        grundrechenarten_erreichte_punkte=grundrechenarten_erreicht,
                        grundrechenarten_max_punkte=grundrechenarten_max,
                        zahlenraum_erreichte_punkte=zahlenraum_erreicht,
                        zahlenraum_max_punkte=zahlenraum_max,
                        gleichungen_erreichte_punkte=gleichungen_erreicht,
                        gleichungen_max_punkte=gleichungen_max,
                        brueche_erreichte_punkte=brueche_erreicht,
                        brueche_max_punkte=brueche_max,
                        gesamt_erreichte_punkte=gesamt_erreichte_punkte,
                        gesamt_max_punkte=gesamt_max_punkte,
                        gesamt_prozent=gesamt_prozent
                    )
                    st.success("Das Testergebnis wurde erfolgreich hinzugefügt.")

    elif choice == "Testergebnisse anzeigen":
        st.subheader("Testergebnisse anzeigen")

        # Abrufen der Teilnehmerliste
        df_teilnehmer = get_all_teilnehmer()
        if df_teilnehmer.empty:
            st.warning("Es sind keine Teilnehmer vorhanden.")
            return

        # Auswahl des Teilnehmers
        teilnehmer_namen = df_teilnehmer['name'].tolist()
        selected_name = st.selectbox("Teilnehmer auswählen", teilnehmer_namen)
        teilnehmer_data = df_teilnehmer[df_teilnehmer['name'] == selected_name].iloc[0]
        teilnehmer_id = teilnehmer_data['teilnehmer_id']

        # Abrufen der Testergebnisse
        df_tests = get_tests_by_teilnehmer(teilnehmer_id)

        if df_tests.empty:
            st.info("Keine Testergebnisse für diesen Teilnehmer vorhanden.")
        else:
            # Testergebnisse anzeigen
            df_tests = sort_dataframe_by_date(df_tests, 'test_datum')
            df_tests_display = df_tests[['test_id', 'test_datum', 'gesamt_erreichte_punkte', 'gesamt_max_punkte', 'gesamt_prozent']]
            df_tests_display['test_datum'] = pd.to_datetime(df_tests_display['test_datum']).dt.strftime('%d.%m.%Y')
            st.dataframe(df_tests_display.set_index('test_id'))

            # Auswahl eines Tests zum Bearbeiten
            test_ids = df_tests['test_id'].tolist()
            selected_test_id = st.selectbox("Testergebnis zum Bearbeiten auswählen (Test-ID)", test_ids)
            test_data = df_tests[df_tests['test_id'] == selected_test_id].iloc[0]

            edit = st.button("Testergebnis bearbeiten")
            delete = st.button("Testergebnis löschen")

            if edit:
                st.subheader(f"Testergebnis vom {format_date(test_data['test_datum'])} bearbeiten")

                # Bearbeitungsformular
                with st.form(key='edit_test_form'):
                    test_datum = st.date_input("Testdatum", datetime.strptime(test_data['test_datum'], '%Y-%m-%d'))

                    st.markdown("#### Punkteingabe pro Kategorie")
                    textaufgaben_erreicht = st.number_input("Erreichte Punkte - Textaufgaben", min_value=0.0, max_value=100.0, value=test_data['textaufgaben_erreichte_punkte'])
                    textaufgaben_max = st.number_input("Maximale Punkte - Textaufgaben", min_value=0.0, max_value=100.0, value=test_data['textaufgaben_max_punkte'])

                    raumvorstellung_erreicht = st.number_input("Erreichte Punkte - Raumvorstellung", min_value=0.0, max_value=100.0, value=test_data['raumvorstellung_erreichte_punkte'])
                    raumvorstellung_max = st.number_input("Maximale Punkte - Raumvorstellung", min_value=0.0, max_value=100.0, value=test_data['raumvorstellung_max_punkte'])

                    grundrechenarten_erreicht = st.number_input("Erreichte Punkte - Grundrechenarten", min_value=0.0, max_value=100.0, value=test_data['grundrechenarten_erreichte_punkte'])
                    grundrechenarten_max = st.number_input("Maximale Punkte - Grundrechenarten", min_value=0.0, max_value=100.0, value=test_data['grundrechenarten_max_punkte'])

                    zahlenraum_erreicht = st.number_input("Erreichte Punkte - Zahlenraum", min_value=0.0, max_value=100.0, value=test_data['zahlenraum_erreichte_punkte'])
                    zahlenraum_max = st.number_input("Maximale Punkte - Zahlenraum", min_value=0.0, max_value=100.0, value=test_data['zahlenraum_max_punkte'])

                    gleichungen_erreicht = st.number_input("Erreichte Punkte - Gleichungen", min_value=0.0, max_value=100.0, value=test_data['gleichungen_erreichte_punkte'])
                    gleichungen_max = st.number_input("Maximale Punkte - Gleichungen", min_value=0.0, max_value=100.0, value=test_data['gleichungen_max_punkte'])

                    brueche_erreicht = st.number_input("Erreichte Punkte - Brüche", min_value=0.0, max_value=100.0, value=test_data['brueche_erreichte_punkte'])
                    brueche_max = st.number_input("Maximale Punkte - Brüche", min_value=0.0, max_value=100.0, value=test_data['brueche_max_punkte'])

                    update_button = st.form_submit_button(label="Änderungen speichern")

                if update_button:
                    # Punkte validieren
                    points_dict = {
                        'textaufgaben': {'erreicht': textaufgaben_erreicht, 'max': textaufgaben_max},
                        'raumvorstellung': {'erreicht': raumvorstellung_erreicht, 'max': raumvorstellung_max},
                        'grundrechenarten': {'erreicht': grundrechenarten_erreicht, 'max': grundrechenarten_max},
                        'zahlenraum': {'erreicht': zahlenraum_erreicht, 'max': zahlenraum_max},
                        'gleichungen': {'erreicht': gleichungen_erreicht, 'max': gleichungen_max},
                        'brueche': {'erreicht': brueche_erreicht, 'max': brueche_max}
                    }

                    if not validate_points({k: v['erreicht'] for k, v in points_dict.items()}):
                        st.error("Bitte geben Sie gültige erreichte Punkte ein.")
                    elif not validate_points({k: v['max'] for k, v in points_dict.items()}):
                        st.error("Bitte geben Sie gültige maximale Punkte ein.")
                    else:
                        # Gesamtsumme der maximalen Punkte prüfen
                        gesamt_max_punkte = sum([v['max'] for v in points_dict.values()])
                        if gesamt_max_punkte != 100:
                            st.error("Die Gesamtsumme der maximalen Punkte muss genau 100 betragen.")
                        else:
                            # Gesamtpunkte und Gesamtprozent berechnen
                            gesamt_erreichte_punkte, _, gesamt_prozent = calculate_total_scores(points_dict)

                            # Aktualisieren des Testergebnisses
                            update_test(
                                test_id=selected_test_id,
                                test_datum=test_datum.strftime('%Y-%m-%d'),
                                textaufgaben_erreichte_punkte=textaufgaben_erreicht,
                                textaufgaben_max_punkte=textaufgaben_max,
                                raumvorstellung_erreichte_punkte=raumvorstellung_erreicht,
                                raumvorstellung_max_punkte=raumvorstellung_max,
                                grundrechenarten_erreichte_punkte=grundrechenarten_erreicht,
                                grundrechenarten_max_punkte=grundrechenarten_max,
                                zahlenraum_erreichte_punkte=zahlenraum_erreicht,
                                zahlenraum_max_punkte=zahlenraum_max,
                                gleichungen_erreichte_punkte=gleichungen_erreicht,
                                gleichungen_max_punkte=gleichungen_max,
                                brueche_erreichte_punkte=brueche_erreicht,
                                brueche_max_punkte=brueche_max,
                                gesamt_erreichte_punkte=gesamt_erreichte_punkte,
                                gesamt_max_punkte=gesamt_max_punkte,
                                gesamt_prozent=gesamt_prozent
                            )
                            st.success("Das Testergebnis wurde erfolgreich aktualisiert.")

            if delete:
                # Bestätigung vor dem Löschen
                confirm = st.warning("Möchten Sie dieses Testergebnis wirklich löschen?")
                if st.button("Ja, löschen"):
                    delete_test(test_id=selected_test_id)
                    st.success("Das Testergebnis wurde erfolgreich gelöscht.")

if __name__ == "__main__":
    main()
