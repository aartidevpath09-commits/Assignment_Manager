import schedule
import time
from datetime import date, timedelta
from db import get_connection
from email_sender import send_email

def check_due_dates():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT a.title, a.due_date, u.email
    FROM assignments a
    JOIN users u ON u.role='student'
    """)
    
    rows = cur.fetchall()

    today = date.today()

    for title, due, email in rows:
        if due == today:
            send_email(
                email,
                "Assignment Due Today",
                f"Your assignment '{title}' is due today!"
            )

    cur.close()
    conn.close()

def start_scheduler():
    schedule.every(1).minutes.do(check_due_dates)

    while True:
        schedule.run_pending()
        time.sleep(1)