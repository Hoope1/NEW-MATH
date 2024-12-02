# app/pages/participants.py

import streamlit as st
import pandas as pd
from datetime import datetime
from app.db_manager import (
    add_teilnehmer,
    get_all_teilnehmer,
    update_teilnehmer,
    delete_teilnehmer
)
from app.utils.helper_functions import (
    validate_sv_nummer,
    validate_dates,
    calculate_status,
    format_date
)

def main():
    st.title("Teilnehmerverwaltung")

    # Menüauswahl
    menu = ["Teilnehmer hinzufügen", "Teilnehmer anzeigen"]
    choice = st.sidebar.selectbox("Aktion auswählen", menu)

    if choice == "Teilnehmer hinzufügen":
        st.subheader("Neuen Teilnehmer hinzufügen")

        # Eingabeformular
        with st.form(key='add_participant_form'):
            name = st.text_input("Name")
            sv_nummer = st.text_input("SV-Nummer (10 Ziffern)")
            geschlecht = st.selectbox("Geschlecht", ["m", "w", "d"])
            eintrittsdatum = st.date_input("Eintrittsdatum", datetime.today())
            austrittsdatum = st.date_input("Austrittsdatum (optional)", None)
            berufsbezeichnung = st.text_input("Berufsbezeichnung (2-10 Großbuchstaben)")

            submit_button = st.form_submit_button(label="Teilnehmer hinzufügen")

        if submit_button:
            # Validierung der Eingaben
            if not name:
                st.error("Bitte den Namen eingeben.")
            elif not validate_sv_nummer(sv_nummer):
                st.error("Die SV-Nummer muss genau 10 Ziffern lang sein.")
            elif not berufsbezeichnung.isupper() or not (2 <= len(berufsbezeichnung) <= 10):
                st.error("Die Berufsbezeichnung muss aus 2-10 Großbuchstaben bestehen.")
            elif not validate_dates(
                eintrittsdatum.strftime("%Y-%m-%d"),
                austrittsdatum.strftime("%Y-%m-%d") if austrittsdatum else None
            ):
                st.error("Das Austrittsdatum muss größer oder gleich dem Eintrittsdatum sein.")
            else:
                # Status berechnen
                status = calculate_status(austrittsdatum.strftime("%Y-%m-%d") if austrittsdatum else None)
                # Teilnehmer hinzufügen
                add_teilnehmer(
                    name=name,
                    sv_nummer=sv_nummer,
                    geschlecht=geschlecht,
                    eintrittsdatum=eintrittsdatum.strftime("%Y-%m-%d"),
                    austrittsdatum=austrittsdatum.strftime("%Y-%m-%d") if austrittsdatum else None,
                    berufsbezeichnung=berufsbezeichnung,
                    status=status
                )
                st.success(f"Teilnehmer '{name}' wurde erfolgreich hinzugefügt.")

    elif choice == "Teilnehmer anzeigen":
        st.subheader("Teilnehmer anzeigen")

        # Statusfilter
        status_filter = st.selectbox("Status filtern", ["Alle", "Aktiv", "Inaktiv"])

        # Teilnehmerdaten abrufen
        df = get_all_teilnehmer()

        if df.empty:
            st.info("Keine Teilnehmer in der Datenbank.")
        else:
            # Daten filtern
            if status_filter != "Alle":
                df = df[df['status'] == status_filter]

            # Anzeige der Teilnehmerliste
            st.dataframe(df[['name', 'sv_nummer', 'geschlecht', 'berufsbezeichnung', 'status']])

            # Auswahl eines Teilnehmers
            teilnehmer_namen = df['name'].tolist()
            selected_name = st.selectbox("Teilnehmer auswählen", teilnehmer_namen)

            if selected_name:
                # Teilnehmerdetails anzeigen
                teilnehmer_data = df[df['name'] == selected_name].iloc[0]

                st.markdown(f"### Details von {teilnehmer_data['name']}")
                st.write(f"**SV-Nummer:** {teilnehmer_data['sv_nummer']}")
                st.write(f"**Geschlecht:** {teilnehmer_data['geschlecht']}")
                st.write(f"**Eintrittsdatum:** {format_date(teilnehmer_data['eintrittsdatum'])}")
                austrittsdatum_formatiert = format_date(teilnehmer_data['austrittsdatum']) if teilnehmer_data['austrittsdatum'] else "N/A"
                st.write(f"**Austrittsdatum:** {austrittsdatum_formatiert}")
                st.write(f"**Berufsbezeichnung:** {teilnehmer_data['berufsbezeichnung']}")
                st.write(f"**Status:** {teilnehmer_data['status']}")

                # Bearbeiten und Löschen
                edit = st.button("Teilnehmer bearbeiten")
                delete = st.button("Teilnehmer löschen")

                if edit:
                    st.subheader(f"Teilnehmer '{teilnehmer_data['name']}' bearbeiten")

                    # Bearbeitungsformular
                    with st.form(key='edit_participant_form'):
                        new_name = st.text_input("Name", value=teilnehmer_data['name'])
                        new_sv_nummer = st.text_input("SV-Nummer (10 Ziffern)", value=teilnehmer_data['sv_nummer'])
                        new_geschlecht = st.selectbox("Geschlecht", ["m", "w", "d"], index=["m", "w", "d"].index(teilnehmer_data['geschlecht']))
                        new_eintrittsdatum = st.date_input(
                            "Eintrittsdatum",
                            datetime.strptime(teilnehmer_data['eintrittsdatum'], "%Y-%m-%d")
                        )
                        new_austrittsdatum = st.date_input(
                            "Austrittsdatum (optional)",
                            datetime.strptime(teilnehmer_data['austrittsdatum'], "%Y-%m-%d") if teilnehmer_data['austrittsdatum'] else None
                        )
                        new_berufsbezeichnung = st.text_input("Berufsbezeichnung (2-10 Großbuchstaben)", value=teilnehmer_data['berufsbezeichnung'])

                        update_button = st.form_submit_button(label="Änderungen speichern")

                    if update_button:
                        # Validierung der Eingaben
                        if not new_name:
                            st.error("Bitte den Namen eingeben.")
                        elif not validate_sv_nummer(new_sv_nummer):
                            st.error("Die SV-Nummer muss genau 10 Ziffern lang sein.")
                        elif not new_berufsbezeichnung.isupper() or not (2 <= len(new_berufsbezeichnung) <= 10):
                            st.error("Die Berufsbezeichnung muss aus 2-10 Großbuchstaben bestehen.")
                        elif not validate_dates(
                            new_eintrittsdatum.strftime("%Y-%m-%d"),
                            new_austrittsdatum.strftime("%Y-%m-%d") if new_austrittsdatum else None
                        ):
                            st.error("Das Austrittsdatum muss größer oder gleich dem Eintrittsdatum sein.")
                        else:
                            # Status neu berechnen
                            new_status = calculate_status(new_austrittsdatum.strftime("%Y-%m-%d") if new_austrittsdatum else None)
                            # Teilnehmerdaten aktualisieren
                            update_teilnehmer(
                                teilnehmer_id=teilnehmer_data['teilnehmer_id'],
                                name=new_name,
                                sv_nummer=new_sv_nummer,
                                geschlecht=new_geschlecht,
                                eintrittsdatum=new_eintrittsdatum.strftime("%Y-%m-%d"),
                                austrittsdatum=new_austrittsdatum.strftime("%Y-%m-%d") if new_austrittsdatum else None,
                                berufsbezeichnung=new_berufsbezeichnung,
                                status=new_status
                            )
                            st.success(f"Teilnehmer '{new_name}' wurde erfolgreich aktualisiert.")

                if delete:
                    # Teilnehmer löschen
                    delete_confirmation = st.warning(f"Möchten Sie den Teilnehmer '{teilnehmer_data['name']}' wirklich löschen?")
                    confirm_delete = st.button("Ja, löschen")
                    if confirm_delete:
                        delete_teilnehmer(teilnehmer_id=teilnehmer_data['teilnehmer_id'])
                        st.success(f"Teilnehmer '{teilnehmer_data['name']}' wurde gelöscht.")

if __name__ == "__main__":
    main()
