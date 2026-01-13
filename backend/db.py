import sqlite3
import os
import json
from datetime import datetime

DB_PATH = "decidekit.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )
    ''')

    # Analyses Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id TEXT PRIMARY KEY,
        user_id INTEGER,
        raw_input TEXT,
        status TEXT,
        verdict TEXT,
        confidence REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_input_tokens INTEGER DEFAULT 0,
        total_output_tokens INTEGER DEFAULT 0,
        original_input TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    # Check for migration
    # Robust Migration: Attempt each column add individually
    columns_to_add = [
        "ALTER TABLE analyses ADD COLUMN total_input_tokens INTEGER DEFAULT 0",
        "ALTER TABLE analyses ADD COLUMN total_output_tokens INTEGER DEFAULT 0",
        "ALTER TABLE analyses ADD COLUMN original_input TEXT",
        "ALTER TABLE analyses ADD COLUMN confidence_metadata TEXT"
    ]
    
    for stmt in columns_to_add:
        try:
            cursor.execute(stmt)
        except sqlite3.OperationalError:
            pass

    # Evidence Signals
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS evidence_signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_id TEXT NOT NULL,
        source_type TEXT,
        platform TEXT,
        pain_theme TEXT,
        description TEXT,
        impact TEXT,
        severity TEXT,
        confidence REAL,
        FOREIGN KEY (analysis_id) REFERENCES analyses (id)
    )
    ''')

    # Pain Clusters
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pain_clusters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_id TEXT NOT NULL,
        cluster_name TEXT,
        severity TEXT,
        description TEXT,
        evidence_count INTEGER,
        FOREIGN KEY (analysis_id) REFERENCES analyses (id)
    )
    ''')

    # Feature Decisions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feature_decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_id TEXT NOT NULL,
        feature_name TEXT,
        mvp_priority BOOLEAN,
        success_metric TEXT,
        complexity TEXT,
        FOREIGN KEY (analysis_id) REFERENCES analyses (id)
    )
    ''')

    # Kill Switch
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kill_switch (
        analysis_id TEXT PRIMARY KEY,
        verdict TEXT,
        confidence REAL,
        primary_reason TEXT,
        failed_criteria TEXT,
        recommendation TEXT,
        FOREIGN KEY (analysis_id) REFERENCES analyses (id)
    )
    ''')
    
    # PRD
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prd (
        analysis_id TEXT PRIMARY KEY,
        content_json TEXT,
        FOREIGN KEY (analysis_id) REFERENCES analyses (id)
    )
    ''')

    # Create default user for v1
    # Check if user exists first
    user = cursor.execute("SELECT * FROM users WHERE username = 'demo'").fetchone()
    if not user:
        # Simple hash or plain text for v1 demo as requested "Hard-coded auth (v1)" 
        # But we'll store it as is for the "hard-coded credentials" part in api.
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                       ('demo', 'demo123'))

    conn.commit()
    conn.close()
    print("Database initialized.")

if __name__ == "__main__":
    init_db()
