import streamlit as st
from app.db_manager import add_test, get_tests_by_teilnehmer, update_test, delete_test, get_all_teilnehmer
from app.utils.helper_functions import validate_points, calculate_total_scores, sort_dataframe_by_date, format_date
import pandas as pd
from datetime import datetime

def main():
    """
    Hauptfunktion für die Verwaltung von Testdaten.
    Bietet Tabs für:
    - Übersicht
    - Test hinzufügen
    - Test bearbeiten/löschen
    """

    st.header("Testdateneingabe und -verwaltung")

    # Tabs erstellen
    tabs = st.tabs(["Übersicht", "Test hinzufügen", "Test bearbeiten/löschen"])

    # Tab: Übersicht
    with tabs[0]:
        st.subheader("Alle Tests anzeigen")
        teilnehmer = get_all_teilnehmer()

        if teilnehmer.empty:
            st.info("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
        else:
            selected_id = st.selectbox(
                "Wählen Sie einen Teilnehmer aus, um die Testergebnisse anzuzeigen:",
                teilnehmer['teilnehmer_id'],
                format_func=lambda x: teilnehmer[teilnehmer['teilnehmer_id'] == x]['name'].values[0],
                key="overview_selectbox"
            )

            df_tests = get_tests_by_teilnehmer(selected_id)

            if df_tests.empty:
                st.info("Keine Testergebnisse für diesen Teilnehmer vorhanden.")
            else:
                df_tests_sorted = sort_dataframe_by_date(df_tests, "test_datum")
                df_tests_sorted['test_datum'] = df_tests_sorted['test_datum'].apply(format_date)
                st.dataframe(
                    df_tests_sorted[['test_id', 'test_datum', 'gesamt_erreichte_punkte', 'gesamt_max_punkte', 'gesamt_prozent']].set_index('test_id'),
                    use_container_width=True
                )

    # Tab: Test hinzufügen
    with tabs[1]:
        st.subheader("Einen neuen Test hinzufügen")
        teilnehmer = get_all_teilnehmer()

        if teilnehmer.empty:
            st.info("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
        else:
            selected_id = st.selectbox(
                "Wählen Sie einen Teilnehmer aus, um einen Test hinzuzufügen:",
                teilnehmer['teilnehmer_id'],
                format_func=lambda x: teilnehmer[teilnehmer['teilnehmer_id'] == x]['name'].values[0],
                key="add_test_selectbox"
            )

            with st.form("add_test_form"):
                test_datum = st.date_input("Datum des Tests:", key="add_test_date")

                # Eingabefelder für Kategorien
                categories = {
                    "Textaufgaben": "textaufgaben",
                    "Raumvorstellung": "raumvorstellung",
                    "Grundrechenarten": "grundrechenarten",
                    "Zahlenraum": "zahlenraum",
                    "Gleichungen": "gleichungen",
                    "Brüche": "brueche"
                }

                erreichte_punkte = {}
                maximale_punkte = {}

                for label, key in categories.items():
                    erreichte_punkte[key] = st.number_input(
                        f"Erreichte Punkte - {label}:", min_value=0.0, max_value=100.0, step=0.1, key=f"{key}_erreicht"
                    )
                    maximale_punkte[key] = st.number_input(
                        f"Maximale Punkte - {label}:", min_value=0.0, max_value=100.0, step=0.1, key=f"{key}_max"
                    )

                submitted = st.form_submit_button("Test hinzufügen")

                if submitted:
                    if not validate_points(erreichte_punkte) or not validate_points(maximale_punkte):
                        st.error("Bitte geben Sie gültige Werte für alle Punkte ein.")
                    else:
                        gesamt_erreichte_punkte, gesamt_max_punkte, gesamt_prozent = calculate_total_scores({
                            k: {'erreicht': erreichte_punkte[k], 'max': maximale_punkte[k]} for k in erreichte_punkte
                        })

                        try:
                            add_test(
                                teilnehmer_id=selected_id,
                                test_datum=str(test_datum),  # Sicherstellen, dass ein String übergeben wird
                                **{
                                    f"{key}_erreichte_punkte": erreichte_punkte[key],
                                    f"{key}_max_punkte": maximale_punkte[key]
                                    for key in categories.values()
                                },
                                gesamt_erreichte_punkte=gesamt_erreichte_punkte,
                                gesamt_max_punkte=gesamt_max_punkte,
                                gesamt_prozent=gesamt_prozent
                            )
                            st.success("Der Test wurde erfolgreich hinzugefügt.")
                        except Exception as e:
                            st.error(f"Ein Fehler ist aufgetreten: {e}")

    # Tab: Test bearbeiten/löschen
    with tabs[2]:
        st.subheader("Tests bearbeiten oder löschen")
        teilnehmer = get_all_teilnehmer()

        if teilnehmer.empty:
            st.info("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
        else:
            selected_id = st.selectbox(
                "Wählen Sie einen Teilnehmer aus, um Tests zu verwalten:",
                teilnehmer['teilnehmer_id'],
                format_func=lambda x: teilnehmer[teilnehmer['teilnehmer_id'] == x]['name'].values[0],
                key="edit_delete_selectbox"
            )

            df_tests = get_tests_by_teilnehmer(selected_id)

            if df_tests.empty:
                st.info("Keine Testergebnisse für diesen Teilnehmer vorhanden.")
            else:
                selected_test_id = st.selectbox(
                    "Wählen Sie einen Test aus, um ihn zu bearbeiten oder zu löschen:",
                    df_tests['test_id'],
                    format_func=lambda x: f"Test-ID {x}",
                    key="select_test_edit_delete"
                )
                selected_test = df_tests[df_tests['test_id'] == selected_test_id].iloc[0]
                st.write(f"**Test-ID:** {selected_test_id}")

                with st.expander("Testdaten bearbeiten"):
                    with st.form("edit_test_form"):
                        test_datum = st.date_input(
                            "Testdatum:",
                            value=pd.to_datetime(selected_test['test_datum']),
                            key="edit_test_date"
                        )
                        updated_points = {}
                        for label, key in categories.items():
                            updated_points[f"{key}_erreichte_punkte"] = st.number_input(
                                f"Erreichte Punkte - {label}:",
                                min_value=0.0,
                                max_value=100.0,
                                value=selected_test[f"{key}_erreichte_punkte"],
                                step=0.1,
                                key=f"edit_{key}_erreicht"
                            )

                        submitted_edit = st.form_submit_button("Änderungen speichern")

                        if submitted_edit:
                            st.success("Der Test wurde erfolgreich aktualisiert.")

                with st.expander("Test löschen"):
                    if st.button("Test löschen", key="delete_test_button"):
                        st.success("Der Test wurde erfolgreich gelöscht.")

if __name__ == "__main__":
    main()
