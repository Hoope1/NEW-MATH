# app/utils/helper_functions.py

import pandas as pd
from datetime import datetime

def validate_sv_nummer(sv_nummer):
    """
    Überprüft, ob die SV-Nummer genau 10 Zeichen lang ist und nur aus Ziffern besteht.

    Args:
        sv_nummer (str): Die zu überprüfende SV-Nummer.

    Returns:
        bool: True, wenn die SV-Nummer gültig ist, sonst False.
    """
    return isinstance(sv_nummer, str) and len(sv_nummer) == 10 and sv_nummer.isdigit()

def validate_dates(eintrittsdatum, austrittsdatum=None):
    """
    Überprüft, ob das Austrittsdatum größer oder gleich dem Eintrittsdatum ist.

    Args:
        eintrittsdatum (str): Eintrittsdatum im Format 'YYYY-MM-DD'.
        austrittsdatum (str): Austrittsdatum im Format 'YYYY-MM-DD' oder None.

    Returns:
        bool: True, wenn die Daten gültig sind, sonst False.
    """
    try:
        eintritt = datetime.strptime(eintrittsdatum, '%Y-%m-%d').date()
        if austrittsdatum:
            austritt = datetime.strptime(austrittsdatum, '%Y-%m-%d').date()
            return austritt >= eintritt
        return True
    except ValueError:
        return False

def calculate_status(austrittsdatum):
    """
    Berechnet den Status ('Aktiv' oder 'Inaktiv') basierend auf dem Austrittsdatum.

    Args:
        austrittsdatum (str): Austrittsdatum im Format 'YYYY-MM-DD' oder None.

    Returns:
        str: 'Aktiv' oder 'Inaktiv'
    """
    if austrittsdatum:
        austritt = datetime.strptime(austrittsdatum, '%Y-%m-%d').date()
        if austritt <= datetime.now().date():
            return 'Inaktiv'
    return 'Aktiv'

def validate_points(points_dict):
    """
    Überprüft, ob alle Punktewerte vorhanden und gültig sind.

    Args:
        points_dict (dict): Dictionary mit Punktenamen als Schlüssel und Punktwerten als Werte.

    Returns:
        bool: True, wenn alle Punkte gültig sind, sonst False.
    """
    for key, value in points_dict.items():
        if value is None or value < 0:
            return False
    return True

def calculate_total_scores(points_dict):
    """
    Berechnet die Gesamtpunkte und den Gesamtprozentsatz basierend auf den erreichten und maximalen Punkten.

    Args:
        points_dict (dict): Dictionary mit Kategorien und ihren erreichten und maximalen Punkten.

    Returns:
        tuple: (gesamt_erreichte_punkte, gesamt_max_punkte, gesamt_prozent)
    """
    gesamt_erreichte_punkte = sum([points_dict[k]['erreicht'] for k in points_dict])
    gesamt_max_punkte = sum([points_dict[k]['max'] for k in points_dict])
    if gesamt_max_punkte > 0:
        gesamt_prozent = (gesamt_erreichte_punkte / gesamt_max_punkte) * 100
    else:
        gesamt_prozent = 0
    return gesamt_erreichte_punkte, gesamt_max_punkte, gesamt_prozent

def format_date(date_str):
    """
    Formatiert ein Datum von 'YYYY-MM-DD' zu 'DD.MM.YYYY'.

    Args:
        date_str (str): Datum im Format 'YYYY-MM-DD'.

    Returns:
        str: Datum im Format 'DD.MM.YYYY'.
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d.%m.%Y')
    except ValueError:
        return date_str

def sort_dataframe_by_date(df, date_column):
    """
    Sortiert einen DataFrame nach einem Datumsspaltenwert.

    Args:
        df (pandas.DataFrame): Der zu sortierende DataFrame.
        date_column (str): Der Name der Datumsspalte.

    Returns:
        pandas.DataFrame: Sortierter DataFrame.
    """
    df[date_column] = pd.to_datetime(df[date_column])
    return df.sort_values(by=date_column)
