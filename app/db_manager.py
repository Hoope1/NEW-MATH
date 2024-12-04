import sqlite3
import pandas as pd
from pathlib import Path
import logging
import streamlit as st

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Cache-Dekorator für die Datenbankverbindung
@st.cache_resource
def get_db_connection():
    """
    Erstellt und cached eine SQLite-Datenbankverbindung.
    Verwendet In-Memory-Datenbank für Streamlit Cloud-Kompatibilität.
    """
    try:
        # In-Memory-Modus für Streamlit Cloud
        conn = sqlite3.connect("file:streamlit_app.db?mode=memory&cache=shared", uri=True)
        logging.info("Datenbankverbindung erfolgreich hergestellt.")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Herstellen der Datenbankverbindung: {e}")
        raise e

def init_db(conn):
    """
    Initialisiert die SQLite-Datenbank:
    Erstellt die Tabellen 'teilnehmer' und 'tests', falls sie nicht existieren.
    """
    try:
        cursor = conn.cursor()

        # Tabelle für Teilnehmer
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
        logging.info("Tabelle 'teilnehmer' erfolgreich erstellt.")

        # Tabelle für Tests
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
        logging.info("Tabellen erfolgreich initialisiert.")
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Initialisieren der Datenbank: {e}")
        raise e

# CRUD-Funktionen
def add_teilnehmer(name, sv_nummer, geschlecht, eintrittsdatum, austrittsdatum, berufsbezeichnung, status):
    """
    Fügt einen neuen Teilnehmer in die Datenbank ein.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO teilnehmer (name, sv_nummer, geschlecht, eintrittsdatum, austrittsdatum, berufsbezeichnung, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, sv_nummer, geschlecht, eintrittsdatum, austrittsdatum, berufsbezeichnung, status))
        conn.commit()
        logging.info(f"Teilnehmer {name} erfolgreich hinzugefügt.")
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Hinzufügen des Teilnehmers {name}: {e}")
        raise e
    finally:
        conn.close()

def get_all_teilnehmer():
    """
    Ruft alle Teilnehmer aus der Datenbank ab.
    """
    conn = get_db_connection()
    try:
        query = "SELECT * FROM teilnehmer"
        df = pd.read_sql_query(query, conn)
        return df
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Abrufen der Teilnehmer: {e}")
        raise e
    finally:
        conn.close()

def update_teilnehmer(teilnehmer_id, name, sv_nummer, geschlecht, eintrittsdatum, austrittsdatum, berufsbezeichnung, status):
    """
    Aktualisiert die Daten eines vorhandenen Teilnehmers.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE teilnehmer
            SET name = ?, sv_nummer = ?, geschlecht = ?, eintrittsdatum = ?, austrittsdatum = ?, berufsbezeichnung = ?, status = ?
            WHERE teilnehmer_id = ?
        ''', (name, sv_nummer, geschlecht, eintrittsdatum, austrittsdatum, berufsbezeichnung, status, teilnehmer_id))
        conn.commit()
        logging.info(f"Teilnehmer {name} erfolgreich aktualisiert.")
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Aktualisieren des Teilnehmers {name}: {e}")
        raise e
    finally:
        conn.close()

def delete_teilnehmer(teilnehmer_id):
    """
    Löscht einen Teilnehmer aus der Datenbank.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM teilnehmer WHERE teilnehmer_id = ?', (teilnehmer_id,))
        conn.commit()
        logging.info(f"Teilnehmer mit ID {teilnehmer_id} erfolgreich gelöscht.")
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Löschen des Teilnehmers mit ID {teilnehmer_id}: {e}")
        raise e
    finally:
        conn.close()

# Initialisierung der Datenbank
conn = get_db_connection()
init_db(conn)
