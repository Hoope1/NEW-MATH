# app/pages/participants.py

import streamlit as st
from app.db_manager import add_teilnehmer, get_all_teilnehmer, update_teilnehmer, delete_teilnehmer
from app.utils.helper_functions import validate_sv_nummer, validate_dates, calculate_status, format_date
import pandas as pd

def main():
    st.header("Teilnehmerverwaltung")
    
    # Tab-Layout: Übersicht, Hinzufügen, Bearbeiten/Löschen
    tabs = st.tabs(["Übersicht", "Teilnehmer hinzufügen", "Teilnehmer bearbeiten/löschen"])
    
    with tabs[0]:
        st.subheader("Alle Teilnehmer")
        df_teilnehmer = get_all_teilnehmer()
        if df_teilnehmer.empty:
            st.info("Keine Teilnehmer vorhanden.")
        else:
            df_display = df_teilnehmer.copy()
            df_display['eintrittsdatum'] = df_display['eintrittsdatum'].apply(format_date)
            df_display['austrittsdatum'] = df_display['austrittsdatum'].apply(lambda x: format_date(x) if x else "")
            st.dataframe(df_display[['teilnehmer_id', 'name', 'sv_nummer', 'geschlecht', 'eintrittsdatum', 'austrittsdatum', 'berufsbezeichnung', 'status']].set_index('teilnehmer_id'))
    
    with tabs[1]:
        st.subheader("Neuen Teilnehmer hinzufügen")
        with st.form("add_participant_form"):
            name = st.text_input("Name", max_chars=100)
            sv_nummer = st.text_input("SV-Nummer", max_chars=10)
            geschlecht = st.selectbox("Geschlecht", ["Männlich", "Weiblich", "Divers"])
            eintrittsdatum = st.date_input("Eintrittsdatum")
            austrittsdatum = st.date_input("Austrittsdatum", value=None)
            berufsbezeichnung = st.text_input("Berufsbezeichnung", max_chars=100)
            status = st.selectbox("Status", ["Aktiv", "Inaktiv"])
            
            submitted = st.form_submit_button("Teilnehmer hinzufügen")
            if submitted:
                if not validate_sv_nummer(sv_nummer):
                    st.error("Die SV-Nummer muss genau 10 Ziffern lang sein.")
                elif not validate_dates(str(eintrittsdatum), str(austrittsdatum)):
                    st.error("Das Austrittsdatum muss größer oder gleich dem Eintrittsdatum sein.")
                else:
                    status_calculated = calculate_status(str(austrittsdatum)) if austrittsdatum else 'Aktiv'
                    try:
                        add_teilnehmer(
                            name=name,
                            sv_nummer=sv_nummer,
                            geschlecht=geschlecht,
                            eintrittsdatum=eintrittsdatum.strftime('%Y-%m-%d'),
                            austrittsdatum=austrittsdatum.strftime('%Y-%m-%d') if austrittsdatum else None,
                            berufsbezeichnung=berufsbezeichnung,
                            status=status_calculated
                        )
                        st.success("Teilnehmer erfolgreich hinzugefügt.")
                    except Exception as e:
                        st.error(f"Fehler beim Hinzufügen des Teilnehmers: {e}")
    
    with tabs[2]:
        st.subheader("Teilnehmer bearbeiten oder löschen")
        df_teilnehmer = get_all_teilnehmer()
        if df_teilnehmer.empty:
            st.info("Keine Teilnehmer vorhanden.")
        else:
            teilnehmer_namen = df_teilnehmer['name'].tolist()
            selected_name = st.selectbox("Teilnehmer auswählen", teilnehmer_namen)
            teilnehmer_data = df_teilnehmer[df_teilnehmer['name'] == selected_name].iloc[0]
            teilnehmer_id = teilnehmer_data['teilnehmer_id']
            
            st.write(f"**Teilnehmer-ID:** {teilnehmer_id}")
            with st.expander("Teilnehmerdaten bearbeiten"):
                with st.form("edit_participant_form"):
                    name = st.text_input("Name", value=teilnehmer_data['name'], max_chars=100)
                    sv_nummer = st.text_input("SV-Nummer", value=teilnehmer_data['sv_nummer'], max_chars=10)
                    geschlecht = st.selectbox("Geschlecht", ["Männlich", "Weiblich", "Divers"], index=["Männlich", "Weiblich", "Divers"].index(teilnehmer_data['geschlecht']))
                    eintrittsdatum = st.date_input("Eintrittsdatum", value=pd.to_datetime(teilnehmer_data['eintrittsdatum']))
                    austrittsdatum = st.date_input("Austrittsdatum", value=pd.to_datetime(teilnehmer_data['austrittsdatum']) if teilnehmer_data['austrittsdatum'] else None)
                    berufsbezeichnung = st.text_input("Berufsbezeichnung", value=teilnehmer_data['berufsbezeichnung'], max_chars=100)
                    status = st.selectbox("Status", ["Aktiv", "Inaktiv"], index=["Aktiv", "Inaktiv"].index(teilnehmer_data['status']))
                    
                    submitted = st.form_submit_button("Teilnehmer aktualisieren")
                    if submitted:
                        if not validate_sv_nummer(sv_nummer):
                            st.error("Die SV-Nummer muss genau 10 Ziffern lang sein.")
                        elif not validate_dates(str(eintrittsdatum), str(austrittsdatum)):
                            st.error("Das Austrittsdatum muss größer oder gleich dem Eintrittsdatum sein.")
                        else:
                            status_calculated = calculate_status(str(austrittsdatum)) if austrittsdatum else 'Aktiv'
                            try:
                                update_teilnehmer(
                                    teilnehmer_id=teilnehmer_id,
                                    name=name,
                                    sv_nummer=sv_nummer,
                                    geschlecht=geschlecht,
                                    eintrittsdatum=eintrittsdatum.strftime('%Y-%m-%d'),
                                    austrittsdatum=austrittsdatum.strftime('%Y-%m-%d') if austrittsdatum else None,
                                    berufsbezeichnung=berufsbezeichnung,
                                    status=status_calculated
                                )
                                st.success("Teilnehmer erfolgreich aktualisiert.")
                            except Exception as e:
                                st.error(f"Fehler beim Aktualisieren des Teilnehmers: {e}")
            
            with st.expander("Teilnehmer löschen"):
                if st.button("Teilnehmer löschen"):
                    try:
                        delete_teilnehmer(teilnehmer_id)
                        st.success("Teilnehmer erfolgreich gelöscht.")
                    except Exception as e:
                        st.error(f"Fehler beim Löschen des Teilnehmers: {e}")
