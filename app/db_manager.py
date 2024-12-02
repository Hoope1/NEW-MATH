import sqlite3
import pandas as pd
from pathlib import Path
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Pfad zur Datenbank
DB_PATH = Path("data/database.db")


def init_db():
    """
    Initialisiert die SQLite-Datenbank:
    Erstellt die Tabellen 'teilnehmer' und 'tests', falls sie nicht existieren.
    """
    try:
        # Sicherstellen, dass das Datenverzeichnis existiert
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        logging.info(f"Verzeichnis {DB_PATH.parent} existiert oder wurde erstellt.")

        # Verbindung zur Datenbank herstellen
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
        logging.info("Tabelle 'teilnehmer' ist bereit.")

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
        logging.info("Tabelle 'tests' ist bereit.")

        conn.commit()
        logging.info("Datenbankinitialisierung abgeschlossen.")
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Initialisieren der Datenbank: {e}")
    finally:
        if conn:
            conn.close()
            logging.info("Datenbankverbindung geschlossen.")


def add_teilnehmer(name, sv_nummer, geschlecht, eintrittsdatum, austrittsdatum, berufsbezeichnung, status):
    """
    Fügt einen neuen Teilnehmer in die Datenbank ein.
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO teilnehmer (name, sv_nummer, geschlecht, eintrittsdatum, austrittsdatum, berufsbezeichnung, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, sv_nummer, geschlecht, eintrittsdatum, austrittsdatum, berufsbezeichnung, status))
        conn.commit()
        logging.info(f"Teilnehmer '{name}' erfolgreich hinzugefügt.")
    except sqlite3.IntegrityError as e:
        logging.error(f"Integritätsfehler beim Hinzufügen des Teilnehmers: {e}")
        raise
    except sqlite3.Error as e:
        logging.error(f"Datenbankfehler beim Hinzufügen des Teilnehmers: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logging.info("Datenbankverbindung geschlossen.")


def get_all_teilnehmer():
    """
    Ruft alle Teilnehmer aus der Datenbank ab.
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        df = pd.read_sql_query('SELECT * FROM teilnehmer', conn)
        logging.info("Alle Teilnehmer erfolgreich abgerufen.")
        return df
    except sqlite3.Error as e:
        logging.error(f"Datenbankfehler beim Abrufen der Teilnehmer: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()
            logging.info("Datenbankverbindung geschlossen.")


def update_teilnehmer(teilnehmer_id, **kwargs):
    """
    Aktualisiert die Daten eines Teilnehmers.
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        columns = ', '.join(f"{key} = ?" for key in kwargs)
        values = list(kwargs.values()) + [teilnehmer_id]
        cursor.execute(f'''
            UPDATE teilnehmer
            SET {columns}
            WHERE teilnehmer_id = ?
        ''', values)
        conn.commit()
        logging.info(f"Teilnehmer-ID {teilnehmer_id} erfolgreich aktualisiert.")
    except sqlite3.Error as e:
        logging.error(f"Datenbankfehler beim Aktualisieren des Teilnehmers: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logging.info("Datenbankverbindung geschlossen.")


def delete_teilnehmer(teilnehmer_id):
    """
    Löscht einen Teilnehmer aus der Datenbank.
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute('DELETE FROM teilnehmer WHERE teilnehmer_id = ?', (teilnehmer_id,))
        conn.commit()
        logging.info(f"Teilnehmer-ID {teilnehmer_id} erfolgreich gelöscht.")
    except sqlite3.Error as e:
        logging.error(f"Datenbankfehler beim Löschen des Teilnehmers: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logging.info("Datenbankverbindung geschlossen.")


def add_test(teilnehmer_id, test_datum, **test_data):
    """
    Fügt ein neues Testergebnis in die Datenbank ein.
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        columns = ', '.join(test_data.keys())
        placeholders = ', '.join('?' for _ in test_data)
        values = list(test_data.values()) + [teilnehmer_id, test_datum]
        cursor.execute(f'''
            INSERT INTO tests (teilnehmer_id, test_datum, {columns})
            VALUES (?, ?, {placeholders})
        ''', [teilnehmer_id, test_datum] + list(test_data.values()))
        conn.commit()
        logging.info(f"Test für Teilnehmer-ID {teilnehmer_id} erfolgreich hinzugefügt.")
    except sqlite3.Error as e:
        logging.error(f"Datenbankfehler beim Hinzufügen des Tests: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logging.info("Datenbankverbindung geschlossen.")


def get_tests_by_teilnehmer(teilnehmer_id):
    """
    Ruft alle Tests eines Teilnehmers aus der Datenbank ab.
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        df = pd.read_sql_query('SELECT * FROM tests WHERE teilnehmer_id = ?', conn, params=(teilnehmer_id,))
        logging.info(f"Testergebnisse für Teilnehmer-ID {teilnehmer_id} erfolgreich abgerufen.")
        return df
    except sqlite3.Error as e:
        logging.error(f"Datenbankfehler beim Abrufen der Testergebnisse: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()
            logging.info("Datenbankverbindung geschlossen.")


def update_test(test_id, **kwargs):
    """
    Aktualisiert ein Testergebnis in der Datenbank.
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        columns = ', '.join(f"{key} = ?" for key in kwargs)
        values = list(kwargs.values()) + [test_id]
        cursor.execute(f'''
            UPDATE tests
            SET {columns}
            WHERE test_id = ?
        ''', values)
        conn.commit()
        logging.info(f"Testergebnis-ID {test_id} erfolgreich aktualisiert.")
    except sqlite3.Error as e:
        logging.error(f"Datenbankfehler beim Aktualisieren des Testergebnisses: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logging.info("Datenbankverbindung geschlossen.")


def delete_test(test_id):
    """
    Löscht ein Testergebnis aus der Datenbank.
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tests WHERE test_id = ?', (test_id,))
        conn.commit()
        logging.info(f"Testergebnis-ID {test_id} erfolgreich gelöscht.")
    except sqlite3.Error as e:
        logging.error(f"Datenbankfehler beim Löschen des Testergebnisses: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logging.info("Datenbankverbindung geschlossen.")


# Datenbank initialisieren
init_db()
