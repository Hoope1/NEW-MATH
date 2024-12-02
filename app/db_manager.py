# app/db_manager.py

import sqlite3
import pandas as pd
from pathlib import Path

# Pfad zur Datenbankdatei
DB_PATH = Path('data/database.db')

# Initialisierung der Datenbank
def init_db():
    # Sicherstellen, dass das Datenverzeichnis existiert
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Verbindung zur SQLite-Datenbank herstellen (Pfad als String)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Tabelle für Teilnehmer erstellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teilnehmer (
            teilnehmer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sv_nummer TEXT UNIQUE NOT NULL,
            geschlecht TEXT NOT NULL,
            eintrittsdatum TEXT NOT NULL,
            austrittsdatum TEXT,
            berufsbezeichnung TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    
    # Tabelle für Tests erstellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tests (
            test_id INTEGER PRIMARY KEY AUTOINCREMENT,
            teilnehmer_id INTEGER NOT NULL,
            test_datum TEXT NOT NULL,
            textaufgaben_erreichte_punkte REAL NOT NULL,
            textaufgaben_max_punkte REAL NOT NULL,
            raumvorstellung_erreichte_punkte REAL NOT NULL,
            raumvorstellung_max_punkte REAL NOT NULL,
            grundrechenarten_erreichte_punkte REAL NOT NULL,
            grundrechenarten_max_punkte REAL NOT NULL,
            zahlenraum_erreichte_punkte REAL NOT NULL,
            zahlenraum_max_punkte REAL NOT NULL,
            gleichungen_erreichte_punkte REAL NOT NULL,
            gleichungen_max_punkte REAL NOT NULL,
            brueche_erreichte_punkte REAL NOT NULL,
            brueche_max_punkte REAL NOT NULL,
            gesamt_erreichte_punkte REAL NOT NULL,
            gesamt_max_punkte REAL NOT NULL,
            gesamt_prozent REAL NOT NULL,
            FOREIGN KEY (teilnehmer_id) REFERENCES teilnehmer(teilnehmer_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Funktion zum Hinzufügen eines neuen Teilnehmers
def add_teilnehmer(name, sv_nummer, geschlecht, eintrittsdatum, austrittsdatum, berufsbezeichnung, status):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO teilnehmer (name, sv_nummer, geschlecht, eintrittsdatum, austrittsdatum, berufsbezeichnung, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, sv_nummer, geschlecht, eintrittsdatum, austrittsdatum, berufsbezeichnung, status))
    conn.commit()
    conn.close()

# Funktion zum Abrufen aller Teilnehmer
def get_all_teilnehmer():
    conn = sqlite3.connect(str(DB_PATH))
    df = pd.read_sql_query('SELECT * FROM teilnehmer', conn)
    conn.close()
    return df

# Funktion zum Aktualisieren eines Teilnehmers
def update_teilnehmer(teilnehmer_id, **kwargs):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    columns = ', '.join(f"{key} = ?" for key in kwargs)
    values = list(kwargs.values())
    values.append(teilnehmer_id)
    cursor.execute(f'''
        UPDATE teilnehmer
        SET {columns}
        WHERE teilnehmer_id = ?
    ''', values)
    conn.commit()
    conn.close()

# Funktion zum Löschen eines Teilnehmers
def delete_teilnehmer(teilnehmer_id):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('DELETE FROM teilnehmer WHERE teilnehmer_id = ?', (teilnehmer_id,))
    conn.commit()
    conn.close()

# Funktion zum Hinzufügen eines Tests
def add_test(teilnehmer_id, test_datum, textaufgaben_erreichte_punkte, textaufgaben_max_punkte,
             raumvorstellung_erreichte_punkte, raumvorstellung_max_punkte,
             grundrechenarten_erreichte_punkte, grundrechenarten_max_punkte,
             zahlenraum_erreichte_punkte, zahlenraum_max_punkte,
             gleichungen_erreichte_punkte, gleichungen_max_punkte,
             brueche_erreichte_punkte, brueche_max_punkte,
             gesamt_erreichte_punkte, gesamt_max_punkte, gesamt_prozent):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tests (
            teilnehmer_id, test_datum,
            textaufgaben_erreichte_punkte, textaufgaben_max_punkte,
            raumvorstellung_erreichte_punkte, raumvorstellung_max_punkte,
            grundrechenarten_erreichte_punkte, grundrechenarten_max_punkte,
            zahlenraum_erreichte_punkte, zahlenraum_max_punkte,
            gleichungen_erreichte_punkte, gleichungen_max_punkte,
            brueche_erreichte_punkte, brueche_max_punkte,
            gesamt_erreichte_punkte, gesamt_max_punkte, gesamt_prozent
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        teilnehmer_id, test_datum,
        textaufgaben_erreichte_punkte, textaufgaben_max_punkte,
        raumvorstellung_erreichte_punkte, raumvorstellung_max_punkte,
        grundrechenarten_erreichte_punkte, grundrechenarten_max_punkte,
        zahlenraum_erreichte_punkte, zahlenraum_max_punkte,
        gleichungen_erreichte_punkte, gleichungen_max_punkte,
        brueche_erreichte_punkte, brueche_max_punkte,
        gesamt_erreichte_punkte, gesamt_max_punkte, gesamt_prozent
    ))
    conn.commit()
    conn.close()

# Funktion zum Abrufen von Tests eines Teilnehmers
def get_tests_by_teilnehmer(teilnehmer_id):
    conn = sqlite3.connect(str(DB_PATH))
    df = pd.read_sql_query('SELECT * FROM tests WHERE teilnehmer_id = ?', conn, params=(teilnehmer_id,))
    conn.close()
    return df

# Funktion zum Aktualisieren eines Tests
def update_test(test_id, **kwargs):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    columns = ', '.join(f"{key} = ?" for key in kwargs)
    values = list(kwargs.values())
    values.append(test_id)
    cursor.execute(f'''
        UPDATE tests
        SET {columns}
        WHERE test_id = ?
    ''', values)
    conn.commit()
    conn.close()

# Funktion zum Löschen eines Tests
def delete_test(test_id):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tests WHERE test_id = ?', (test_id,))
    conn.commit()
    conn.close()

# Initialisierung der Datenbank beim ersten Import
init_db()
