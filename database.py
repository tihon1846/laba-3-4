import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "poliklinika.db")


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database(scheme_file="scheme.sql"):
    conn = get_connection()
    cursor = conn.cursor()

    scheme_path = os.path.join(BASE_DIR, scheme_file)

    with open(scheme_path, "r", encoding="utf-8") as file:
        scheme = file.read()

    cursor.executescript(scheme)

    conn.commit()
    conn.close()