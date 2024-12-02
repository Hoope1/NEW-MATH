# app/pages/reports.py

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from app.db_manager import get_all_teilnehmer, get_tests_by_teilnehmer
from app.utils.helper_functions import format_date, sort_dataframe_by_date
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook
import tempfile

def create_pdf_report(teilnehmer_data, df_tests, avg_last_two):
    """
    Erstellt einen PDF-Bericht für einen Teilnehmer.
    
    Args:
        teilnehmer_data (pandas.Series): Daten des Teilnehmers.
        df_tests (pandas.DataFrame): Testergebnisse des Teilnehmers.
        avg_last_two (float): Durchschnitt der letzten zwei Testergebnisse.
    
    Returns:
        bytes: PDF-Datei als Bytes.
    """
    buffer = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(buffer.name, pagesize=letter)
    width, height = letter

    # Titel
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, f"Bericht für {teilnehmer_data['name']}")

    # Teilnehmerdaten
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"SV-Nummer: {teilnehmer_data['sv_nummer']}")
    c.drawString(50, height - 120, f"Eintrittsdatum: {format_date(teilnehmer_data['eintrittsdatum'])}")
    austrittsdatum = format_date(teilnehmer_data['austrittsdatum']) if teilnehmer_data['austrittsdatum'] else "Nicht angegeben"
    c.drawString(50, height - 140, f"Austrittsdatum: {austrittsdatum}")
    c.drawString(50, height - 160, f"Berufsbezeichnung: {teilnehmer_data['berufsbezeichnung']}")
    c.drawString(50, height - 180, f"Status: {teilnehmer_data['status']}")

    # Testergebnisse
    c.drawString(50, height - 220, "Testergebnisse:")
    y = height - 240
    for index, test in df_tests.iterrows():
        c.drawString(60, y, f"Testdatum: {format_date(test['test_datum'])}, Gesamtprozente: {test['gesamt_prozent']:.2f}%")
        y -= 20

    # Durchschnitt der letzten zwei Tests
    c.drawString(50, y - 20, f"Durchschnitt der letzten zwei Tests: {avg_last_two:.2f}%")

    c.save()

    with open(buffer.name, "rb") as f:
        pdf_bytes = f.read()

    os.unlink(buffer.name)
    return pdf_bytes

def create_excel_report(teilnehmer_data, df_tests, avg_last_two):
    """
    Erstellt einen Excel-Bericht für einen Teilnehmer.
    
    Args:
        teilnehmer_data (pandas.Series): Daten des Teilnehmers.
        df_tests (pandas.DataFrame): Testergebnisse des Teilnehmers.
        avg_last_two (float): Durchschnitt der letzten zwei Testergebnisse.
    
    Returns:
        bytes: Excel-Datei als Bytes.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Bericht"

    # Titel
    ws.append([f"Bericht für {teilnehmer_data['name']}"])
    ws.append([])

    # Teilnehmerdaten
    ws.append(["SV-Nummer", teilnehmer_data['sv_nummer']])
    ws.append(["Eintrittsdatum", format_date(teilnehmer_data['eintrittsdatum'])])
    austrittsdatum = format_date(teilnehmer_data['austrittsdatum']) if teilnehmer_data['austrittsdatum'] else "Nicht angegeben"
    ws.append(["Austrittsdatum", austrittsdatum])
    ws.append(["Berufsbezeichnung", teilnehmer_data['berufsbezeichnung']])
    ws.append(["Status", teilnehmer_data['status']])
    ws.append([])

    # Testergebnisse
    ws.append(["Testergebnisse"])
    ws.append(["Testdatum", "Gesamtprozente"])
    for index, test in df_tests.iterrows():
        ws.append([format_date(test['test_datum']), f"{test['gesamt_prozent']:.2f}%"])
    
    ws.append([])
    ws.append(["Durchschnitt der letzten zwei Tests", f"{avg_last_two:.2f}%"])

    # Speichern in einem temporären Puffer
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        wb.save(tmp.name)
        with open(tmp.name, "rb") as f:
            excel_bytes = f.read()
    os.unlink(tmp.name)
    return excel_bytes

def main():
    st.header("Berichterstellung")
    
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

    # Abrufen der Testergebnisse
    df_tests = get_tests_by_teilnehmer(teilnehmer_id)

    if df_tests.empty:
        st.info("Keine Testergebnisse für diesen Teilnehmer vorhanden.")
        return

    # Sortieren der Testergebnisse nach Datum
    df_tests = sort_dataframe_by_date(df_tests, 'test_datum')

    # Durchschnitt der letzten zwei Tests berechnen
    if len(df_tests) >= 2:
        last_two = df_tests.tail(2)
        avg_last_two = last_two['gesamt_prozent'].mean()
    else:
        avg_last_two = df_tests['gesamt_prozent'].mean()

    # Berichtserstellung Buttons
    st.subheader("Bericht erstellen")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("PDF-Bericht erstellen"):
            try:
                pdf_bytes = create_pdf_report(teilnehmer_data, df_tests, avg_last_two)
                st.success("PDF-Bericht wurde erstellt.")
                st.download_button(
                    label="PDF herunterladen",
                    data=pdf_bytes,
                    file_name=f"{selected_name}_Bericht.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Fehler beim Erstellen des PDF-Berichts: {e}")
    with col2:
        if st.button("Excel-Bericht erstellen"):
            try:
                excel_bytes = create_excel_report(teilnehmer_data, df_tests, avg_last_two)
                st.success("Excel-Bericht wurde erstellt.")
                st.download_button(
                    label="Excel herunterladen",
                    data=excel_bytes,
                    file_name=f"{selected_name}_Bericht.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Fehler beim Erstellen des Excel-Berichts: {e}")

    st.markdown("---")

    # Anzeige der Testergebnisse im Detail
    st.subheader("Testergebnisse Übersicht")
    df_tests_display = df_tests.copy()
    df_tests_display['test_datum'] = df_tests_display['test_datum'].apply(format_date)
    st.dataframe(df_tests_display[['test_datum', 'gesamt_erreichte_punkte', 'gesamt_max_punkte', 'gesamt_prozent']].set_index('test_datum'))

    st.markdown("---")

    # Hinweise zur Berichterstellung
    st.markdown("""
    ### Hinweise zur Berichterstellung
    - **PDF-Bericht:** Enthält Teilnehmerdaten, alle Testergebnisse und den Durchschnitt der letzten zwei Tests.
    - **Excel-Bericht:** Bietet eine tabellarische Übersicht der Testergebnisse sowie Teilnehmerdaten und Durchschnittswerte.
    - **Download:** Nach der Erstellung können die Berichte direkt heruntergeladen werden.
    """)

