import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="assignment_db",
        user="postgres",
        password="root"
    )