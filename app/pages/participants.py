import streamlit as st
from app.db_manager import add_teilnehmer, get_all_teilnehmer, update_teilnehmer, delete_teilnehmer
from app.utils.helper_functions import validate_sv_nummer, validate_dates, calculate_status, format_date
import pandas as pd

def main():
    """
    Hauptfunktion zur Verwaltung von Teilnehmern.
    Diese Funktion bietet Tabs für:
    - Übersicht
    - Teilnehmer hinzufügen
    - Teilnehmer bearbeiten/löschen
    """

    st.header("Teilnehmerverwaltung")
    tabs = st.tabs(["Übersicht", "Teilnehmer hinzufügen", "Teilnehmer bearbeiten/löschen"])

    # Tab: Übersicht
    with tabs[0]:
        st.subheader("Alle Teilnehmer anzeigen")
        df_teilnehmer = get_all_teilnehmer()

        if df_teilnehmer.empty:
            st.info("Keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
        else:
            # Formatieren der Datumsfelder
            df_teilnehmer['Eintrittsdatum'] = df_teilnehmer['eintrittsdatum'].apply(format_date)
            df_teilnehmer['Austrittsdatum'] = df_teilnehmer['austrittsdatum'].apply(
                lambda x: format_date(x) if x else "Nicht angegeben"
            )
            # Teilnehmer anzeigen
            st.dataframe(
                df_teilnehmer[['teilnehmer_id', 'name', 'sv_nummer', 'geschlecht', 'Eintrittsdatum', 'Austrittsdatum',
                               'berufsbezeichnung', 'status']].set_index('teilnehmer_id'),
                use_container_width=True
            )
            # Schalter für inaktive Teilnehmer
            if st.checkbox("Inaktive Teilnehmer anzeigen"):
                st.write(df_teilnehmer[df_teilnehmer['status'] == 'Inaktiv'])

    # Tab: Teilnehmer hinzufügen
    with tabs[1]:
        st.subheader("Einen neuen Teilnehmer hinzufügen")
        with st.form("add_participant_form"):
            name = st.text_input("Name des Teilnehmers:", max_chars=100)
            sv_nummer = st.text_input("SV-Nummer (10 Ziffern):", max_chars=10)
            geschlecht = st.selectbox("Geschlecht des Teilnehmers:", ["Männlich", "Weiblich", "Divers"])
            eintrittsdatum = st.date_input("Eintrittsdatum:", key="add_entry_date")
            austrittsdatum = st.date_input("Austrittsdatum (optional):", key="add_exit_date", value=None)
            berufsbezeichnung = st.text_input("Berufsbezeichnung:", max_chars=100)

            submitted = st.form_submit_button("Teilnehmer hinzufügen")
            if submitted:
                if not validate_sv_nummer(sv_nummer):
                    st.error("Die SV-Nummer muss genau 10 Ziffern lang sein.")
                elif not validate_dates(str(eintrittsdatum), str(austrittsdatum) if austrittsdatum else None):
                    st.error("Das Austrittsdatum muss größer oder gleich dem Eintrittsdatum sein.")
                else:
                    status_calculated = calculate_status(str(austrittsdatum)) if austrittsdatum else 'Aktiv'
                    try:
                        add_teilnehmer(
                            name=name,
                            sv_nummer=sv_nummer,
                            geschlecht=geschlecht,
                            eintrittsdatum=str(eintrittsdatum),
                            austrittsdatum=str(austrittsdatum) if austrittsdatum else None,
                            berufsbezeichnung=berufsbezeichnung,
                            status=status_calculated
                        )
                        st.success(f"Teilnehmer '{name}' wurde erfolgreich hinzugefügt.")
                    except Exception as e:
                        st.error(f"Fehler beim Hinzufügen des Teilnehmers: {e}")

    # Tab: Teilnehmer bearbeiten/löschen
    with tabs[2]:
        st.subheader("Teilnehmer bearbeiten oder löschen")
        df_teilnehmer = get_all_teilnehmer()

        if df_teilnehmer.empty:
            st.info("Keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
        else:
            teilnehmer_namen = df_teilnehmer['name'].tolist()
            selected_name = st.selectbox("Wählen Sie einen Teilnehmer aus:", teilnehmer_namen, key="edit_selectbox")
            teilnehmer_data = df_teilnehmer[df_teilnehmer['name'] == selected_name].iloc[0]
            teilnehmer_id = teilnehmer_data['teilnehmer_id']

            with st.expander("Teilnehmerdaten bearbeiten"):
                with st.form("edit_participant_form"):
                    name = st.text_input("Name des Teilnehmers:", value=teilnehmer_data['name'], max_chars=100)
                    sv_nummer = st.text_input("SV-Nummer (10 Ziffern):", value=teilnehmer_data['sv_nummer'], max_chars=10)
                    geschlecht = st.selectbox(
                        "Geschlecht des Teilnehmers:", 
                        ["Männlich", "Weiblich", "Divers"],
                        index=["Männlich", "Weiblich", "Divers"].index(teilnehmer_data['geschlecht'])
                    )
                    eintrittsdatum = st.date_input("Eintrittsdatum:", value=pd.to_datetime(teilnehmer_data['eintrittsdatum']))
                    austrittsdatum = st.date_input(
                        "Austrittsdatum (optional):", 
                        value=pd.to_datetime(teilnehmer_data['austrittsdatum']) if teilnehmer_data['austrittsdatum'] else None
                    )
                    berufsbezeichnung = st.text_input("Berufsbezeichnung:", value=teilnehmer_data['berufsbezeichnung'], max_chars=100)
                    submitted_edit = st.form_submit_button("Änderungen speichern")

                    if submitted_edit:
                        if not validate_sv_nummer(sv_nummer):
                            st.error("Die SV-Nummer muss genau 10 Ziffern lang sein.")
                        elif not validate_dates(str(eintrittsdatum), str(austrittsdatum) if austrittsdatum else None):
                            st.error("Das Austrittsdatum muss größer oder gleich dem Eintrittsdatum sein.")
                        else:
                            status_calculated = calculate_status(str(austrittsdatum)) if austrittsdatum else 'Aktiv'
                            try:
                                update_teilnehmer(
                                    teilnehmer_id=teilnehmer_id,
                                    name=name,
                                    sv_nummer=sv_nummer,
                                    geschlecht=geschlecht,
                                    eintrittsdatum=str(eintrittsdatum),
                                    austrittsdatum=str(austrittsdatum) if austrittsdatum else None,
                                    berufsbezeichnung=berufsbezeichnung,
                                    status=status_calculated
                                )
                                st.success("Die Änderungen wurden erfolgreich gespeichert.")
                            except Exception as e:
                                st.error(f"Fehler beim Aktualisieren des Teilnehmers: {e}")

            with st.expander("Teilnehmer löschen"):
                if st.button("Teilnehmer löschen", key="delete_button"):
                    try:
                        delete_teilnehmer(teilnehmer_id)
                        st.success(f"Teilnehmer '{selected_name}' wurde erfolgreich gelöscht.")
                    except Exception as e:
                        st.error(f"Fehler beim Löschen des Teilnehmers: {e}")

if __name__ == "__main__":
    main()
