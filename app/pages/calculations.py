# app/pages/calculations.py

import streamlit as st
import pandas as pd
from app.db_manager import get_all_teilnehmer, get_tests_by_teilnehmer
from app.utils.helper_functions import sort_dataframe_by_date, format_date


def calculate_average_total(df_tests):
    """
    Berechnet den durchschnittlichen Gesamtprozentsatz aus den Testergebnissen.
    
    Args:
        df_tests (pandas.DataFrame): DataFrame mit Testergebnissen.
        
    Returns:
        float: Durchschnittlicher Gesamtprozentsatz.
    """
    if df_tests.empty:
        return 0
    return df_tests['gesamt_prozent'].mean()


def main():
    """
    Hauptfunktion für automatische Berechnungen und Validierung:
    Berechnet Durchschnittswerte, identifiziert beste und schlechteste Ergebnisse und analysiert die Leistung.
    """
    st.header("Automatische Berechnungen und Validierung")

    st.markdown("""
    ### Übersicht der Berechnungen
    - **Durchschnittliche Gesamtleistung** pro Teilnehmer.
    - **Beste und schlechteste Testergebnisse**.
    - **Leistungsentwicklung** über die Zeit.
    - **Kategorische Analyse** der erreichten Punkte.
    """)

    # Teilnehmerdaten abrufen
    df_teilnehmer = get_all_teilnehmer()
    if df_teilnehmer.empty:
        st.warning("Es sind keine Teilnehmer vorhanden. Bitte fügen Sie zuerst Teilnehmer hinzu.")
        return

    # Teilnehmerauswahl
    teilnehmer_name = st.selectbox("Teilnehmer auswählen für detaillierte Berechnungen", df_teilnehmer['name'].tolist())
    teilnehmer_data = df_teilnehmer[df_teilnehmer['name'] == teilnehmer_name].iloc[0]
    teilnehmer_id = teilnehmer_data['teilnehmer_id']

    # Testergebnisse abrufen
    df_tests = get_tests_by_teilnehmer(teilnehmer_id)

    if df_tests.empty:
        st.info("Keine Testergebnisse für diesen Teilnehmer vorhanden.")
    else:
        # Testergebnisse sortieren
        df_tests = sort_dataframe_by_date(df_tests, 'test_datum')

        # Übersicht der Testergebnisse
        st.subheader("Testergebnisse Übersicht")
        df_display = df_tests.copy()
        df_display['test_datum'] = df_display['test_datum'].apply(format_date)
        st.dataframe(
            df_display[['test_id', 'test_datum', 'gesamt_erreichte_punkte', 'gesamt_max_punkte', 'gesamt_prozent']].set_index('test_id'),
            use_container_width=True
        )

        # Durchschnittliche Gesamtleistung berechnen
        st.subheader("Berechnungen")
        durchschnitt = calculate_average_total(df_tests)
        st.metric(label="Durchschnittliche Gesamtleistung", value=f"{durchschnitt:.2f}%")

        # Bestes und schlechtestes Ergebnis ermitteln
        best_test = df_tests.loc[df_tests['gesamt_prozent'].idxmax()]
        worst_test = df_tests.loc[df_tests['gesamt_prozent'].idxmin()]
        st.write(f"**Bestes Testergebnis:** {format_date(best_test['test_datum'])} mit {best_test['gesamt_prozent']:.2f}%")
        st.write(f"**Schlechtestes Testergebnis:** {format_date(worst_test['test_datum'])} mit {worst_test['gesamt_prozent']:.2f}%")

        # Leistungsentwicklung über die Zeit visualisieren
        st.subheader("Leistungsentwicklung über die Zeit")
        st.line_chart(df_tests.set_index('test_datum')['gesamt_prozent'])

        # Kategorische Analyse
        st.subheader("Kategorische Analyse der erreichten Punkte")
        categories = ['textaufgaben', 'raumvorstellung', 'grundrechenarten', 'zahlenraum', 'gleichungen', 'brueche']
        category_means = {category: df_tests[f"{category}_erreichte_punkte"].mean() for category in categories}
        category_max = {category: df_tests[f"{category}_max_punkte"].mean() for category in categories}
        category_percentages = {
            category: (category_means[category] / category_max[category]) * 100 if category_max[category] > 0 else 0
            for category in categories
        }

        df_category = pd.DataFrame({
            'Kategorie': list(category_percentages.keys()),
            'Durchschnittliche Prozentwerte': list(category_percentages.values())
        })

        st.bar_chart(df_category.set_index('Kategorie'))

    # Allgemeine Statistiken über alle Teilnehmer
    st.markdown("---")
    st.subheader("Allgemeine Statistiken")
    if st.checkbox("Allgemeine Statistiken anzeigen"):
        all_teilnehmer_ids = df_teilnehmer['teilnehmer_id'].tolist()
        all_tests = pd.concat([get_tests_by_teilnehmer(t_id) for t_id in all_teilnehmer_ids if not get_tests_by_teilnehmer(t_id).empty])

        if all_tests.empty():
            st.info("Keine Testergebnisse vorhanden.")
        else:
            st.markdown("#### Gesamtanzahl der Tests")
            total_tests = all_tests.shape[0]
            st.metric(label="Gesamtanzahl der Tests", value=total_tests)

            st.markdown("#### Durchschnittliche Punkte pro Kategorie")
            avg_points = {category: all_tests[f"{category}_erreichte_punkte"].mean() for category in categories}
            avg_max_points = {category: all_tests[f"{category}_max_punkte"].mean() for category in categories}
            avg_percentages = {
                category: (avg_points[category] / avg_max_points[category]) * 100 if avg_max_points[category] > 0 else 0
                for category in categories
            }

            df_avg = pd.DataFrame({
                'Kategorie': list(avg_percentages.keys()),
                'Durchschnittliche Prozentwerte': list(avg_percentages.values())
            })

            st.bar_chart(df_avg.set_index('Kategorie'))

            st.markdown("#### Gesamtsumme der Punkte")
            total_erreicht = all_tests['gesamt_erreichte_punkte'].sum()
            total_max = all_tests['gesamt_max_punkte'].sum()
            overall_percentage = (total_erreicht / total_max) * 100 if total_max > 0 else 0
            st.metric(label="Gesamt erreichte Punkte", value=total_erreicht)
            st.metric(label="Gesamt maximale Punkte", value=total_max)
            st.metric(label="Gesamter Prozentwert", value=f"{overall_percentage:.2f}%")


if __name__ == "__main__":
    main()
