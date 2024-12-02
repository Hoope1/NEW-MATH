# app/pages/tests.py

import streamlit as st
from app.db_manager import add_test, get_tests_by_teilnehmer, update_test, delete_test, get_all_teilnehmer
from app.utils.helper_functions import validate_points, calculate_total_scores, sort_dataframe_by_date, format_date
import pandas as pd
from datetime import datetime

def main():
    st.header("Testdateneingabe und -verwaltung")
    
    # Tab-Layout: Übersicht, Test hinzufügen, Test bearbeiten/löschen
    tabs = st.tabs(["Übersicht", "Test hinzufügen", "Test bearbeiten/löschen"])
    
    with tabs[0]:
        st.subheader("Alle Tests")
        teilnehmer = get_all_teilnehmer()
        if teilnehmer.empty:
            st.info("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
        else:
            selected_id = st.selectbox("Teilnehmer auswählen", teilnehmer['teilnehmer_id'], format_func=lambda x: teilnehmer[teilnehmer['teilnehmer_id'] == x]['name'].values[0])
            df_tests = get_tests_by_teilnehmer(selected_id)
            if df_tests.empty:
                st.info("Keine Testergebnisse für diesen Teilnehmer vorhanden.")
            else:
                df_display = df_tests.copy()
                df_display['test_datum'] = df_display['test_datum'].apply(format_date)
                st.dataframe(df_display[['test_id', 'test_datum', 'gesamt_erreichte_punkte', 'gesamt_max_punkte', 'gesamt_prozent']].set_index('test_id'))
    
    with tabs[1]:
        st.subheader("Neuen Test hinzufügen")
        teilnehmer = get_all_teilnehmer()
        if teilnehmer.empty:
            st.info("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
        else:
            selected_id = st.selectbox("Teilnehmer auswählen", teilnehmer['teilnehmer_id'], format_func=lambda x: teilnehmer[teilnehmer['teilnehmer_id'] == x]['name'].values[0])
            with st.form("add_test_form"):
                test_datum = st.date_input("Testdatum")
                textaufgaben_erreichte_punkte = st.number_input("Erreichte Punkte - Textaufgaben", min_value=0.0, max_value=100.0, step=0.1)
                textaufgaben_max_punkte = st.number_input("Maximale Punkte - Textaufgaben", min_value=0.0, max_value=100.0, step=0.1)
                
                raumvorstellung_erreichte_punkte = st.number_input("Erreichte Punkte - Raumvorstellung", min_value=0.0, max_value=100.0, step=0.1)
                raumvorstellung_max_punkte = st.number_input("Maximale Punkte - Raumvorstellung", min_value=0.0, max_value=100.0, step=0.1)
                
                grundrechenarten_erreichte_punkte = st.number_input("Erreichte Punkte - Grundrechenarten", min_value=0.0, max_value=100.0, step=0.1)
                grundrechenarten_max_punkte = st.number_input("Maximale Punkte - Grundrechenarten", min_value=0.0, max_value=100.0, step=0.1)
                
                zahlenraum_erreichte_punkte = st.number_input("Erreichte Punkte - Zahlenraum", min_value=0.0, max_value=100.0, step=0.1)
                zahlenraum_max_punkte = st.number_input("Maximale Punkte - Zahlenraum", min_value=0.0, max_value=100.0, step=0.1)
                
                gleichungen_erreichte_punkte = st.number_input("Erreichte Punkte - Gleichungen", min_value=0.0, max_value=100.0, step=0.1)
                gleichungen_max_punkte = st.number_input("Maximale Punkte - Gleichungen", min_value=0.0, max_value=100.0, step=0.1)
                
                brueche_erreichte_punkte = st.number_input("Erreichte Punkte - Brüche", min_value=0.0, max_value=100.0, step=0.1)
                brueche_max_punkte = st.number_input("Maximale Punkte - Brüche", min_value=0.0, max_value=100.0, step=0.1)
                
                submitted = st.form_submit_button("Test hinzufügen")
                if submitted:
                    points_dict_erreicht = {
                        'textaufgaben': textaufgaben_erreichte_punkte,
                        'raumvorstellung': raumvorstellung_erreichte_punkte,
                        'grundrechenarten': grundrechenarten_erreichte_punkte,
                        'zahlenraum': zahlenraum_erreichte_punkte,
                        'gleichungen': gleichungen_erreichte_punkte,
                        'brueche': brueche_erreichte_punkte
                    }
                    
                    points_dict_max = {
                        'textaufgaben': textaufgaben_max_punkte,
                        'raumvorstellung': raumvorstellung_max_punkte,
                        'grundrechenarten': grundrechenarten_max_punkte,
                        'zahlenraum': zahlenraum_max_punkte,
                        'gleichungen': gleichungen_max_punkte,
                        'brueche': brueche_max_punkte
                    }
                    
                    if not validate_points(points_dict_erreicht):
                        st.error("Bitte geben Sie gültige erreichte Punkte ein.")
                    elif not validate_points(points_dict_max):
                        st.error("Bitte geben Sie gültige maximale Punkte ein.")
                    else:
                        # Gesamtsumme der maximalen Punkte prüfen
                        gesamt_max_punkte = sum(points_dict_max.values())
                        if gesamt_max_punkte != 100:
                            st.error("Die Gesamtsumme der maximalen Punkte muss genau 100 betragen.")
                        else:
                            # Gesamtpunkte und Gesamtprozentsatz berechnen
                            points_dict = {
                                'textaufgaben': {'erreicht': textaufgaben_erreichte_punkte, 'max': textaufgaben_max_punkte},
                                'raumvorstellung': {'erreicht': raumvorstellung_erreichte_punkte, 'max': raumvorstellung_max_punkte},
                                'grundrechenarten': {'erreicht': grundrechenarten_erreichte_punkte, 'max': grundrechenarten_max_punkte},
                                'zahlenraum': {'erreicht': zahlenraum_erreichte_punkte, 'max': zahlenraum_max_punkte},
                                'gleichungen': {'erreicht': gleichungen_erreichte_punkte, 'max': gleichungen_max_punkte},
                                'brueche': {'erreicht': brueche_erreichte_punkte, 'max': brueche_max_punkte}
                            }
                            
                            gesamt_erreichte_punkte, gesamt_max_punkte, gesamt_prozent = calculate_total_scores(points_dict)
                            
                            try:
                                add_test(
                                    teilnehmer_id=selected_id,
                                    test_datum=test_datum.strftime('%Y-%m-%d'),
                                    textaufgaben_erreichte_punkte=textaufgaben_erreichte_punkte,
                                    textaufgaben_max_punkte=textaufgaben_max_punkte,
                                    raumvorstellung_erreichte_punkte=raumvorstellung_erreichte_punkte,
                                    raumvorstellung_max_punkte=raumvorstellung_max_punkte,
                                    grundrechenarten_erreichte_punkte=grundrechenarten_erreichte_punkte,
                                    grundrechenarten_max_punkte=grundrechenarten_max_punkte,
                                    zahlenraum_erreichte_punkte=zahlenraum_erreichte_punkte,
                                    zahlenraum_max_punkte=zahlenraum_max_punkte,
                                    gleichungen_erreichte_punkte=gleichungen_erreichte_punkte,
                                    gleichungen_max_punkte=gleichungen_max_punkte,
                                    brueche_erreichte_punkte=brueche_erreichte_punkte,
                                    brueche_max_punkte=brueche_max_punkte,
                                    gesamt_erreichte_punkte=gesamt_erreichte_punkte,
                                    gesamt_max_punkte=gesamt_max_punkte,
                                    gesamt_prozent=gesamt_prozent
                                )
                                st.success("Test erfolgreich hinzugefügt.")
                            except Exception as e:
                                st.error(f"Fehler beim Hinzufügen des Tests: {e}")

    with tabs[2]:
        st.subheader("Test bearbeiten oder löschen")
        teilnehmer = get_all_teilnehmer()
        if teilnehmer.empty:
            st.info("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
        else:
            selected_id = st.selectbox("Teilnehmer auswählen", teilnehmer['teilnehmer_id'], format_func=lambda x: teilnehmer[teilnehmer['teilnehmer_id'] == x]['name'].values[0])
            df_tests = get_tests_by_teilnehmer(selected_id)
            if df_tests.empty:
                st.info("Keine Testergebnisse für diesen Teilnehmer vorhanden.")
            else:
                test_ids = df_tests['test_id'].tolist()
                selected_test_id = st.selectbox("Test auswählen", test_ids)
                selected_test = df_tests[df_tests['test_id'] == selected_test_id].iloc[0]
                
                st.write(f"**Test-ID:** {selected_test_id}")
                with st.expander("Testdaten bearbeiten"):
                    with st.form("edit_test_form"):
                        test_datum = st.date_input("Testdatum", value=pd.to_datetime(selected_test['test_datum']))
                        textaufgaben_erreichte_punkte = st.number_input("Erreichte Punkte - Textaufgaben", min_value=0.0, max_value=100.0, value=selected_test['textaufgaben_erreichte_punkte'], step=0.1)
                        textaufgaben_max_punkte = st.number_input("Maximale Punkte - Textaufgaben", min_value=0.0, max_value=100.0, value=selected_test['textaufgaben_max_punkte'], step=0.1)
                        
                        raumvorstellung_erreichte_punkte = st.number_input("Erreichte Punkte - Raumvorstellung", min_value=0.0, max_value=100.0, value=selected_test['raumvorstellung_erreichte_punkte'], step=0.1)
                        raumvorstellung_max_punkte = st.number_input("Maximale Punkte - Raumvorstellung", min_value=0.0, max_value=100.0, value=selected_test['raumvorstellung_max_punkte'], step=0.1)
                        
                        grundrechenarten_erreichte_punkte = st.number_input("Erreichte Punkte - Grundrechenarten", min_value=0.0, max_value=100.0, value=selected_test['grundrechenarten_erreichte_punkte'], step=0.1)
                        grundrechenarten_max_punkte = st.number_input("Maximale Punkte - Grundrechenarten", min_value=0.0, max_value=100.0, value=selected_test['grundrechenarten_max_punkte'], step=0.1)
                        
                        zahlenraum_erreichte_punkte = st.number_input("Erreichte Punkte - Zahlenraum", min_value=0.0, max_value=100.0, value=selected_test['zahlenraum_erreichte_punkte'], step=0.1)
                        zahlenraum_max_punkte = st.number_input("Maximale Punkte - Zahlenraum", min_value=0.0, max_value=100.0, value=selected_test['zahlenraum_max_punkte'], step=0.1)
                        
                        gleichungen_erreichte_punkte = st.number_input("Erreichte Punkte - Gleichungen", min_value=0.0, max_value=100.0, value=selected_test['gleichungen_erreichte_punkte'], step=0.1)
                        gleichungen_max_punkte = st.number_input("Maximale Punkte - Gleichungen", min_value=0.0, max_value=100.0, value=selected_test['gleichungen_max_punkte'], step=0.1)
                        
                        brueche_erreichte_punkte = st.number_input("Erreichte Punkte - Brüche", min_value=0.0, max_value=100.0, value=selected_test['brueche_erreichte_punkte'], step=0.1)
                        brueche_max_punkte = st.number_input("Maximale Punkte - Brüche", min_value=0.0, max_value=100.0, value=selected_test['brueche_max_punkte'], step=0.1)
                        
                        submitted = st.form_submit_button("Test aktualisieren")
                        if submitted:
                            points_dict_erreicht = {
                                'textaufgaben': textaufgaben_erreichte_punkte,
                                'raumvorstellung': raumvorstellung_erreichte_punkte,
                                'grundrechenarten': grundrechenarten_erreichte_punkte,
                                'zahlenraum': zahlenraum_erreichte_punkte,
                                'gleichungen': gleichungen_erreichte_punkte,
                                'brueche': brueche_erreichte_punkte
                            }
                            
                            points_dict_max = {
                                'textaufgaben': textaufgaben_max_punkte,
                                'raumvorstellung': raumvorstellung_max_punkte,
                                'grundrechenarten': grundrechenarten_max_punkte,
                                'zahlenraum': zahlenraum_max_punkte,
                                'gleichungen': gleichungen_max_punkte,
                                'brueche': brueche_max_punkte
                            }
                            
                            if not validate_points(points_dict_erreicht):
                                st.error("Bitte geben Sie gültige erreichte Punkte ein.")
                            elif not validate_points(points_dict_max):
                                st.error("Bitte geben Sie gültige maximale Punkte ein.")
                            else:
                                # Gesamtsumme der maximalen Punkte prüfen
                                gesamt_max_punkte = sum(points_dict_max.values())
                                if gesamt_max_punkte != 100:
                                    st.error("Die Gesamtsumme der maximalen Punkte muss genau 100 betragen.")
                                else:
                                    # Gesamtpunkte und Gesamtprozentsatz berechnen
                                    points_dict = {
                                        'textaufgaben': {'erreicht': textaufgaben_erreichte_punkte, 'max': textaufgaben_max_punkte},
                                        'raumvorstellung': {'erreicht': raumvorstellung_erreichte_punkte, 'max': raumvorstellung_max_punkte},
                                        'grundrechenarten': {'erreicht': grundrechenarten_erreichte_punkte, 'max': grundrechenarten_max_punkte},
                                        'zahlenraum': {'erreicht': zahlenraum_erreichte_punkte, 'max': zahlenraum_max_punkte},
                                        'gleichungen': {'erreicht': gleichungen_erreichte_punkte, 'max': gleichungen_max_punkte},
                                        'brueche': {'erreicht': brueche_erreichte_punkte, 'max': brueche_max_punkte}
                                    }
                                    
                                    gesamt_erreichte_punkte, gesamt_max_punkte, gesamt_prozent = calculate_total_scores(points_dict)
                                    
                                    try:
                                        update_test(
                                            test_id=selected_test_id,
                                            test_datum=test_datum.strftime('%Y-%m-%d'),
                                            textaufgaben_erreichte_punkte=textaufgaben_erreichte_punkte,
                                            textaufgaben_max_punkte=textaufgaben_max_punkte,
                                            raumvorstellung_erreichte_punkte=raumvorstellung_erreichte_punkte,
                                            raumvorstellung_max_punkte=raumvorstellung_max_punkte,
                                            grundrechenarten_erreichte_punkte=grundrechenarten_erreichte_punkte,
                                            grundrechenarten_max_punkte=grundrechenarten_max_punkte,
                                            zahlenraum_erreichte_punkte=zahlenraum_erreichte_punkte,
                                            zahlenraum_max_punkte=zahlenraum_max_punkte,
                                            gleichungen_erreichte_punkte=gleichungen_erreichte_punkte,
                                            gleichungen_max_punkte=gleichungen_max_punkte,
                                            brueche_erreichte_punkte=brueche_erreichte_punkte,
                                            brueche_max_punkte=brueche_max_punkte,
                                            gesamt_erreichte_punkte=gesamt_erreichte_punkte,
                                            gesamt_max_punkte=gesamt_max_punkte,
                                            gesamt_prozent=gesamt_prozent
                                        )
                                        st.success("Test erfolgreich aktualisiert.")
                                    except Exception as e:
                                        st.error(f"Fehler beim Aktualisieren des Tests: {e}")
                
                with st.expander("Test löschen"):
                    if st.button("Test löschen"):
                        try:
                            delete_test(selected_test_id)
                            st.success("Test erfolgreich gelöscht.")
                        except Exception as e:
                            st.error(f"Fehler beim Löschen des Tests: {e}")
