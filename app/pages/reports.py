import streamlit as st
from app.db_manager import get_tests_by_teilnehmer, get_all_teilnehmer
from app.utils.helper_functions import sort_dataframe_by_date, calculate_age
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from openpyxl import Workbook
import pandas as pd
import os

def main():
    """
    Hauptfunktion zur Erstellung von Berichten in PDF- und Excel-Format.
    Ermöglicht den Export von Teilnehmerdaten und Testergebnissen.
    """
    st.header("Berichterstellung")
    st.markdown("""
        Wählen Sie einen Teilnehmer aus, um einen Bericht zu generieren. 
        Der Bericht enthält Teilnehmerinformationen, Testergebnisse und Statistiken.
    """)

    teilnehmer_data = get_all_teilnehmer()
    
    if teilnehmer_data.empty:
        st.info("Keine Teilnehmerdaten vorhanden. Bitte fügen Sie Teilnehmer hinzu.")
        return

    selected_id = st.selectbox(
        "Wählen Sie einen Teilnehmer aus:",
        teilnehmer_data['teilnehmer_id'],
        format_func=lambda x: teilnehmer_data[teilnehmer_data['teilnehmer_id'] == x]['name'].values[0],
        key="select_report_participant"
    )

    df_tests = get_tests_by_teilnehmer(selected_id)

    if df_tests.empty:
        st.info("Keine Testdaten für diesen Teilnehmer vorhanden.")
        return

    # Teilnehmerinformationen
    selected_participant = teilnehmer_data[teilnehmer_data['teilnehmer_id'] == selected_id].iloc[0]
    age = calculate_age(selected_participant['sv_nummer'])
    st.subheader("Teilnehmerinformationen")
    st.write(f"**Name:** {selected_participant['name']}")
    st.write(f"**Alter:** {age}")
    st.write(f"**Status:** {selected_participant['status']}")

    # Testdaten vorbereiten
    df_tests_sorted = sort_dataframe_by_date(df_tests, "test_datum")
    df_tests_sorted['test_datum'] = df_tests_sorted['test_datum'].apply(lambda x: x.strftime('%d.%m.%Y'))

    # Bericht exportieren
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Bericht als PDF exportieren"):
            pdf_path = generate_pdf_report(selected_participant, df_tests_sorted)
            st.success(f"PDF-Bericht wurde erfolgreich erstellt: {pdf_path}")

    with col2:
        if st.button("Bericht als Excel exportieren"):
            excel_path = generate_excel_report(selected_participant, df_tests_sorted)
            st.success(f"Excel-Bericht wurde erfolgreich erstellt: {excel_path}")

def generate_pdf_report(participant, test_data):
    """
    Generiert einen PDF-Bericht für einen Teilnehmer.
    Args:
        participant (dict): Informationen über den Teilnehmer.
        test_data (DataFrame): Testergebnisse des Teilnehmers.
    Returns:
        str: Pfad zur generierten PDF-Datei.
    """
    pdf_path = f"{participant['name']}-Bericht.pdf"
    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()
    story = []

    # Teilnehmerinformationen
    story.append(Paragraph(f"Bericht für: {participant['name']}", styles['Title']))
    story.append(Paragraph(f"Alter: {calculate_age(participant['sv_nummer'])}", styles['Normal']))
    story.append(Paragraph(f"Status: {participant['status']}", styles['Normal']))
    story.append(Paragraph(" ", styles['Normal']))

    # Testergebnisse
    data = [["Datum", "Erreichte Punkte", "Maximale Punkte", "Prozent"]]
    for index, row in test_data.iterrows():
        data.append([
            row['test_datum'],
            row['gesamt_erreichte_punkte'],
            row['gesamt_max_punkte'],
            f"{row['gesamt_prozent']:.2f}%"
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table)

    # PDF speichern
    doc.build(story)
    return pdf_path

def generate_excel_report(participant, test_data):
    """
    Generiert einen Excel-Bericht für einen Teilnehmer.
    Args:
        participant (dict): Informationen über den Teilnehmer.
        test_data (DataFrame): Testergebnisse des Teilnehmers.
    Returns:
        str: Pfad zur generierten Excel-Datei.
    """
    excel_path = f"{participant['name']}-Bericht.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Bericht"

    # Teilnehmerinformationen
    ws.append(["Name", participant['name']])
    ws.append(["Alter", calculate_age(participant['sv_nummer'])])
    ws.append(["Status", participant['status']])
    ws.append([])

    # Testergebnisse
    ws.append(["Datum", "Erreichte Punkte", "Maximale Punkte", "Prozent"])
    for index, row in test_data.iterrows():
        ws.append([
            row['test_datum'],
            row['gesamt_erreichte_punkte'],
            row['gesamt_max_punkte'],
            f"{row['gesamt_prozent']:.2f}%"
        ])

    # Excel speichern
    wb.save(excel_path)
    return excel_path

if __name__ == "__main__":
    main()
