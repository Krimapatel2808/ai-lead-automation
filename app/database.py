import sqlite3

DATABASE_NAME = "leads.db"


def create_database():
    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT NOT NULL,
            message TEXT NOT NULL,
            lead_score INTEGER NOT NULL,
            priority TEXT NOT NULL,
            action TEXT NOT NULL,
            requirement TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_lead(
    name,
    company,
    message,
    lead_score,
    priority,
    action,
    requirement
):
    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO leads (
            name,
            company,
            message,
            lead_score,
            priority,
            action,
            requirement
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        company,
        message,
        lead_score,
        priority,
        action,
        requirement
    ))

    connection.commit()
    connection.close()