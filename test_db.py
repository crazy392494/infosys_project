import sqlite3

def check_db():
    try:
        conn = sqlite3.connect('career_platform.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs")
        jobs = cursor.fetchall()
        print(f"Total jobs: {len(jobs)}")
        for j in jobs[:3]:
            print(f"{j['id']}. {j['title']} @ {j['company']}")
    except Exception as e:
        print("Error:", e)

check_db()
