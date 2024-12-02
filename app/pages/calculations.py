# app/pages/calculations.py

import streamlit as st
import pandas as pd
from app.db_manager import get_all_teilnehmer, get_tests_by_teilnehmer
from app.utils.helper_functions import sort_dataframe_by_date, format_date


def calculate_average_total(df_tests):
    """
    Berechnet die durchschnittliche Gesamtleistung eines Teilnehmers.
    """
    if df_tests.empty:
        return 0.0
    return df_tests['gesamt_prozent'].mean()


def calculate_category_averages(df_tests):
    """
    Berechnet die durchschnittlichen Prozentwerte für jede Kategorie.
    """
    categories = ['textaufgaben', 'raumvorstellung', 'grundrechenarten', 'zahlenraum', 'gleichungen', 'brueche']
    averages = {
        category: (df_tests[f"{category}_erreichte_punkte"].mean() / df_tests[f"{category}_max_punkte"].mean() * 100)
        if df_tests[f"{category}_max_punkte"].mean() > 0 else 0.0
        for category in categories
    }
    return averages


def main():
    """
    Hauptfunktion für Berechnungen und Validierungen.
    Ermöglicht die Anzeige von Teilnehmerleistungen und allgemeinen Statistiken.
    """
    st.header("Automatische Berechnungen und Validierung")

    st.markdown("""
    ### Übersicht der Berechnungen
    - Durchschnittliche Gesamtleistung pro Teilnehmer.
    - Beste und schlechteste Testergebnisse.
    - Leistungsentwicklung über die Zeit.
    - Analyse der Kategorienpunkte.
    """)

    # Teilnehmerdaten abrufen
    df_teilnehmer = get_all_teilnehmer()
    if df_teilnehmer.empty:
        st.warning("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie Teilnehmer hinzu.")
        return

    teilnehmer_name = st.selectbox("Teilnehmer auswählen", df_teilnehmer['name'].tolist())
    teilnehmer_data = df_teilnehmer[df_teilnehmer['name'] == teilnehmer_name].iloc[0]
    teilnehmer_id = teilnehmer_data['teilnehmer_id']

    # Testergebnisse des Teilnehmers abrufen
    df_tests = get_tests_by_teilnehmer(teilnehmer_id)

    if df_tests.empty:
        st.info("Keine Testergebnisse für diesen Teilnehmer vorhanden.")
    else:
        # Daten sortieren
        df_tests = sort_dataframe_by_date(df_tests, 'test_datum')

        # Testergebnisse anzeigen
        st.subheader("Testergebnisse Übersicht")
        df_tests_display = df_tests.copy()
        df_tests_display['test_datum'] = df_tests_display['test_datum'].apply(format_date)
        st.dataframe(
            df_tests_display[['test_id', 'test_datum', 'gesamt_erreichte_punkte', 'gesamt_max_punkte', 'gesamt_prozent']].set_index('test_id'),
            use_container_width=True
        )

        # Berechnungen durchführen
        st.subheader("Berechnungen")

        # Durchschnittliche Gesamtleistung
        durchschnitt = calculate_average_total(df_tests)
        st.metric(label="Durchschnittliche Gesamtleistung", value=f"{durchschnitt:.2f}%")

        # Bestes und schlechtestes Testergebnis
        best_test = df_tests.loc[df_tests['gesamt_prozent'].idxmax()]
        worst_test = df_tests.loc[df_tests['gesamt_prozent'].idxmin()]
        st.write(f"**Bestes Testergebnis:** {format_date(best_test['test_datum'])} mit {best_test['gesamt_prozent']:.2f}%")
        st.write(f"**Schlechtestes Testergebnis:** {format_date(worst_test['test_datum'])} mit {worst_test['gesamt_prozent']:.2f}%")

        # Leistungsentwicklung
        st.subheader("Leistungsentwicklung über die Zeit")
        st.line_chart(df_tests.set_index('test_datum')['gesamt_prozent'])

        # Kategorienanalyse
        st.subheader("Kategorische Analyse der erreichten Punkte")
        category_averages = calculate_category_averages(df_tests)
        df_category = pd.DataFrame({
            "Kategorie": list(category_averages.keys()),
            "Durchschnittliche Prozentwerte": list(category_averages.values())
        })
        st.bar_chart(df_category.set_index("Kategorie"))

    # Allgemeine Statistiken für alle Teilnehmer
    st.markdown("---")
    st.subheader("Allgemeine Statistiken")
    if st.checkbox("Allgemeine Statistiken anzeigen"):
        all_teilnehmer_ids = df_teilnehmer['teilnehmer_id'].tolist()
        all_tests = pd.concat([
            get_tests_by_teilnehmer(t_id) for t_id in all_teilnehmer_ids
            if not get_tests_by_teilnehmer(t_id).empty
        ])

        if all_tests.empty:
            st.info("Keine Testergebnisse vorhanden.")
        else:
            st.markdown("#### Gesamtanzahl der Tests")
            total_tests = all_tests.shape[0]
            st.metric(label="Gesamtanzahl der Tests", value=total_tests)

            st.markdown("#### Durchschnittliche Punkte pro Kategorie")
            category_averages_all = calculate_category_averages(all_tests)
            df_avg = pd.DataFrame({
                "Kategorie": list(category_averages_all.keys()),
                "Durchschnittliche Prozentwerte": list(category_averages_all.values())
            })
            st.bar_chart(df_avg.set_index("Kategorie"))

            st.markdown("#### Gesamtsumme der Punkte")
            total_erreicht = all_tests['gesamt_erreichte_punkte'].sum()
            total_max = all_tests['gesamt_max_punkte'].sum()
            overall_percentage = (total_erreicht / total_max) * 100 if total_max > 0 else 0
            st.metric(label="Gesamt erreichte Punkte", value=total_erreicht)
            st.metric(label="Gesamt maximale Punkte", value=total_max)
            st.metric(label="Gesamter Prozentwert", value=f"{overall_percentage:.2f}%")


if __name__ == "__main__":
    main()
