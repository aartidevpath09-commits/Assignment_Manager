from db import cursor, conn

def create_tables():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        id SERIAL PRIMARY KEY,
        title TEXT,
        description TEXT,
        due_date DATE,
        created_by INT
    );
    """)

    conn.commit()