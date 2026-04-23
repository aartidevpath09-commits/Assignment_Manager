import schedule
import time
from db import cursor

def check_due():
    cursor.execute("SELECT * FROM assignments WHERE due_date = CURRENT_DATE")
    data = cursor.fetchall()

    for a in data:
        print("Reminder: Assignment Due Today ->", a[1])

def start_scheduler():
    schedule.every().day.at("09:00").do(check_due)

    while True:
        schedule.run_pending()
        time.sleep(60)