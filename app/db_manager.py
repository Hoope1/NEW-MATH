import sqlite3
import pandas as pd
from pathlib import Path
import logging

# Konfiguration des Loggings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Pfad zur Datenbankdatei
DB_PATH = Path('data/database.db')


def init_db():
    """
    Initialisiert die Datenbank, indem die erforderlichen Tabellen erstellt werden, falls sie nicht existieren.
    """
    try:
        # Sicherstellen, dass das Datenverzeichnis existiert
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        logging.info(f"Verzeichnis {DB_PATH.parent} existiert oder wurde erstellt.")

        # Verbindung zur SQLite-Datenbank herstellen
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            logging.info("Verbindung zur SQLite-Datenbank hergestellt.")

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
            logging.info("Tabelle 'teilnehmer' wurde überprüft oder erstellt.")

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
            logging.info("Tabelle 'tests' wurde überprüft oder erstellt.")

        logging.info("Datenbankinitialisierung abgeschlossen.")
    except sqlite3.Error as e:
        logging.error(f"Fehler bei der Datenbankinitialisierung: {e}")


def add_teilnehmer(name, sv_nummer, geschlecht, eintrittsdatum, austrittsdatum, berufsbezeichnung, status):
    """
    Fügt einen neuen Teilnehmer in die Datenbank ein.
    """
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO teilnehmer (name, sv_nummer, geschlecht, eintrittsdatum, austrittsdatum, berufsbezeichnung, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, sv_nummer, geschlecht, eintrittsdatum, austrittsdatum, berufsbezeichnung, status))
            conn.commit()
            logging.info(f"Teilnehmer '{name}' erfolgreich hinzugefügt.")
    except sqlite3.IntegrityError:
        logging.error(f"Teilnehmer mit SV-Nummer '{sv_nummer}' existiert bereits.")
        raise ValueError(f"Teilnehmer mit der SV-Nummer '{sv_nummer}' existiert bereits.")
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Hinzufügen eines Teilnehmers: {e}")
        raise


def get_all_teilnehmer():
    """
    Ruft alle Teilnehmer aus der Datenbank ab.
    """
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            df = pd.read_sql_query('SELECT * FROM teilnehmer', conn)
            logging.info("Alle Teilnehmer erfolgreich abgerufen.")
            return df
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Abrufen der Teilnehmer: {e}")
        return pd.DataFrame()


def update_teilnehmer(teilnehmer_id, **kwargs):
    """
    Aktualisiert die Daten eines Teilnehmers basierend auf der Teilnehmer-ID.
    """
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
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
            logging.info(f"Teilnehmer mit ID {teilnehmer_id} erfolgreich aktualisiert.")
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Aktualisieren eines Teilnehmers: {e}")
        raise


def delete_teilnehmer(teilnehmer_id):
    """
    Löscht einen Teilnehmer aus der Datenbank basierend auf der Teilnehmer-ID.
    """
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM teilnehmer WHERE teilnehmer_id = ?', (teilnehmer_id,))
            conn.commit()
            logging.info(f"Teilnehmer mit ID {teilnehmer_id} erfolgreich gelöscht.")
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Löschen eines Teilnehmers: {e}")
        raise


def add_test(teilnehmer_id, test_datum, **categories):
    """
    Fügt ein neues Testergebnis für einen Teilnehmer hinzu.
    """
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            columns = ', '.join(categories.keys())
            placeholders = ', '.join(['?'] * len(categories))
            values = [teilnehmer_id, test_datum] + list(categories.values())
            cursor.execute(f'''
                INSERT INTO tests (teilnehmer_id, test_datum, {columns})
                VALUES (?, ?, {placeholders})
            ''', values)
            conn.commit()
            logging.info(f"Testergebnis für Teilnehmer-ID {teilnehmer_id} erfolgreich hinzugefügt.")
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Hinzufügen eines Testergebnisses: {e}")
        raise


def get_tests_by_teilnehmer(teilnehmer_id):
    """
    Ruft alle Tests eines Teilnehmers basierend auf der Teilnehmer-ID ab.
    """
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            df = pd.read_sql_query(
                'SELECT * FROM tests WHERE teilnehmer_id = ?',
                conn,
                params=(teilnehmer_id,)
            )
            logging.info(f"Testergebnisse für Teilnehmer-ID {teilnehmer_id} erfolgreich abgerufen.")
            return df
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Abrufen der Testergebnisse: {e}")
        return pd.DataFrame()


def update_test(test_id, **kwargs):
    """
    Aktualisiert die Daten eines Tests basierend auf der Test-ID.
    """
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
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
            logging.info(f"Testergebnis mit ID {test_id} erfolgreich aktualisiert.")
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Aktualisieren eines Testergebnisses: {e}")
        raise


def delete_test(test_id):
    """
    Löscht ein Testergebnis basierend auf der Test-ID.
    """
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tests WHERE test_id = ?', (test_id,))
            conn.commit()
            logging.info(f"Testergebnis mit ID {test_id} erfolgreich gelöscht.")
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Löschen eines Testergebnisses: {e}")
        raise


# Initialisierung der Datenbank beim Import
init_db()
