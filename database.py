import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="parking_lot.db"):
        self.db_name = db_name
        self.create_table()

    def create_table(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detected_plates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT,
                detected_time TEXT
            )        ''')
        conn.commit()
        conn.close()

    def add_detected_plate(self, plate_number):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        detected_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO detected_plates (plate_number, detected_time) 
            VALUES (?, ?)
        ''', (plate_number, detected_time))
        conn.commit()
        conn.close()
        print(f"[DATABASE] Plate '{plate_number}' stored in database.")

    def get_all_detected_plates(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM detected_plates")
        records = cursor.fetchall()
        conn.close()
        return records
if __name__ == "__main__":
    db = Database()

    # Add some plates
    db.add_detected_plate("LEF 13 9052")
    db.add_detected_plate("AVE 068")

    # Retrieve and display all plates
    plates = db.get_all_detected_plates()
    for plate in plates:
        print(plate)

