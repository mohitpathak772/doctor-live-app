import os
import sqlite3

try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    """Postgres (cloud) ya SQLite (local) connection deta hai"""
    if DATABASE_URL and HAS_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect("doctors.db")


def ph():
    """SQL placeholder - Postgres: %s, SQLite: ?"""
    return "%s" if DATABASE_URL else "?"


def create_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    if DATABASE_URL:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                degree TEXT,
                hospital_name TEXT NOT NULL,
                hospital_type TEXT NOT NULL,
                city TEXT NOT NULL,
                medicines TEXT,
                is_present INTEGER DEFAULT 0
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                degree TEXT,
                hospital_name TEXT NOT NULL,
                hospital_type TEXT NOT NULL,
                city TEXT NOT NULL,
                medicines TEXT,
                is_present INTEGER DEFAULT 0
            )
        """)
    conn.commit()
    conn.close()
    print("✅ Database ready!")


def add_sample_doctors():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM doctors")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"ℹ️ {count} doctors already exist.")
        conn.close()
        return

    sample_doctors = [
        ("Dr. Rajesh Sharma", "General Physician", "MBBS, MD", "AIIMS Delhi", "Government", "Delhi", "Paracetamol, Amoxicillin, Cetirizine"),
        ("Dr. Priya Verma", "Cardiologist", "MBBS, MD, DM", "Safdarjung Hospital", "Government", "Delhi", "Aspirin, Atorvastatin, Metoprolol"),
        ("Dr. Amit Kumar", "Orthopedic", "MBBS, MS", "Apollo Hospital", "Private", "Delhi", "Ibuprofen, Calcium, Vitamin D3"),
        ("Dr. Sunita Reddy", "Pediatrician", "MBBS, MD", "Max Hospital", "Private", "Delhi", "Paracetamol Syrup, ORS, Zinc"),
        ("Dr. Mohammad Ali", "Dermatologist", "MBBS, MD", "Ram Manohar Lohia Hospital", "Government", "Delhi", "Clotrimazole, Betnovate, Cetirizine"),
    ]
    
    p = ph()
    for doc in sample_doctors:
        cursor.execute(f"""
            INSERT INTO doctors 
            (name, specialization, degree, hospital_name, hospital_type, city, medicines)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p})
        """, doc)
        
    conn.commit()
    conn.close()
    print(f"✅ {len(sample_doctors)} doctors added!")


if __name__ == "__main__":
    create_database()
    add_sample_doctors()