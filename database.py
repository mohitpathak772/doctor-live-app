# ============================================
# database.py
# Complete Database - Users + Doctors + Blood Banks
#                    + Checkup Centers + Medical Stores
# ============================================

import os
import sqlite3
import secrets
import random
from datetime import datetime

try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    """Postgres (cloud) ya SQLite (local) connection"""
    if DATABASE_URL and HAS_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect("doctors.db")


def ph():
    """SQL placeholder"""
    return "%s" if DATABASE_URL else "?"


def generate_token():
    """Unique token - 12 random characters (letters + numbers)"""
    return secrets.token_urlsafe(12)


def generate_otp():
    """6-digit OTP"""
    return str(random.randint(100000, 999999))


# ============================================
# Create All Tables
# ============================================

def create_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # USERS TABLE
    if DATABASE_URL:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                mobile TEXT UNIQUE NOT NULL,
                language TEXT DEFAULT 'hi',
                location TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otps (
                id SERIAL PRIMARY KEY,
                mobile TEXT NOT NULL,
                otp TEXT NOT NULL,
                created_at TEXT
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mobile TEXT UNIQUE NOT NULL,
                language TEXT DEFAULT 'hi',
                location TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mobile TEXT NOT NULL,
                otp TEXT NOT NULL,
                created_at TEXT
            )
        """)
    
    # DOCTORS TABLE
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
                is_present INTEGER DEFAULT 0,
                token TEXT,
                hospital_lat REAL,
                hospital_lng REAL
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
                is_present INTEGER DEFAULT 0,
                token TEXT,
                hospital_lat REAL,
                hospital_lng REAL
            )
        """)
    
    # BLOOD BANKS
    if DATABASE_URL:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blood_banks (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                phone TEXT,
                distance_km REAL DEFAULT 0,
                is_open INTEGER DEFAULT 0,
                opening_time TEXT,
                closing_time TEXT,
                blood_groups TEXT
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blood_banks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                phone TEXT,
                distance_km REAL DEFAULT 0,
                is_open INTEGER DEFAULT 0,
                opening_time TEXT,
                closing_time TEXT,
                blood_groups TEXT
            )
        """)
    
    # CHECKUP CENTERS
    if DATABASE_URL:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkup_centers (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                phone TEXT,
                distance_km REAL DEFAULT 0,
                is_open INTEGER DEFAULT 0,
                opening_time TEXT,
                closing_time TEXT,
                checkups TEXT,
                price_range TEXT
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkup_centers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                phone TEXT,
                distance_km REAL DEFAULT 0,
                is_open INTEGER DEFAULT 0,
                opening_time TEXT,
                closing_time TEXT,
                checkups TEXT,
                price_range TEXT
            )
        """)
    
    # MEDICAL STORES
    if DATABASE_URL:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_stores (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                phone TEXT,
                distance_km REAL DEFAULT 0,
                is_open INTEGER DEFAULT 0,
                opening_time TEXT,
                closing_time TEXT,
                services TEXT
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_stores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                phone TEXT,
                distance_km REAL DEFAULT 0,
                is_open INTEGER DEFAULT 0,
                opening_time TEXT,
                closing_time TEXT,
                services TEXT
            )
        """)
    
    conn.commit()
    conn.close()
    print("✅ Saari tables ready hain!")


# ============================================
# Sample Data
# ============================================

def add_sample_doctors():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM doctors")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"ℹ️  {count} doctors already hain.")
        conn.close()
        return
    
    # (name, spec, degree, hospital, type, city, medicines, lat, lng)
    sample = [
        ("Dr. Rajesh Sharma", "General Physician", "MBBS, MD",
         "AIIMS Delhi", "Government", "Delhi",
         "Paracetamol, Amoxicillin, Cetirizine",
         28.5672, 77.2100),
        
        ("Dr. Priya Verma", "Cardiologist", "MBBS, MD, DM",
         "Safdarjung Hospital", "Government", "Delhi",
         "Aspirin, Atorvastatin, Metoprolol",
         28.5675, 77.2065),
        
        ("Dr. Amit Kumar", "Orthopedic", "MBBS, MS",
         "Apollo Hospital", "Private", "Delhi",
         "Ibuprofen, Calcium, Vitamin D3",
         28.5445, 77.2812),
        
        ("Dr. Sunita Reddy", "Pediatrician", "MBBS, MD",
         "Max Hospital", "Private", "Delhi",
         "Paracetamol Syrup, ORS, Zinc",
         28.5355, 77.2100),
        
        ("Dr. Mohammad Ali", "Dermatologist", "MBBS, MD",
         "Ram Manohar Lohia Hospital", "Government", "Delhi",
         "Clotrimazole, Betnovate, Cetirizine",
         28.6289, 77.2077),
    ]
    
    p = ph()
    for name, spec, deg, hosp, htype, city, meds, lat, lng in sample:
        token = generate_token()
        cursor.execute(f"""
            INSERT INTO doctors 
            (name, specialization, degree, hospital_name, hospital_type, 
             city, medicines, token, hospital_lat, hospital_lng)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
        """, (name, spec, deg, hosp, htype, city, meds, token, lat, lng))
    
    conn.commit()
    conn.close()
    print(f"✅ {len(sample)} doctors add ho gaye!")


def add_sample_blood_banks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM blood_banks")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    banks = [
        ("Red Cross Blood Bank", "1 Red Cross Road, Connaught Place",
         "Delhi", "+91-11-23716434", 2.5, 1, "9:00 AM", "6:00 PM",
         "A+, B+, O+, AB+, O-, A-"),
        ("AIIMS Blood Bank", "Ansari Nagar, AIIMS Campus",
         "Delhi", "+91-11-26588500", 4.8, 1, "24 Hours", "24 Hours",
         "All Blood Groups"),
        ("City Blood Bank", "45 Karol Bagh Main Road",
         "Delhi", "+91-11-28751234", 6.2, 0, "10:00 AM", "5:00 PM",
         "A+, B+, O+"),
        ("Apollo Blood Bank", "Sarita Vihar, Mathura Road",
         "Delhi", "+91-11-26925858", 8.5, 1, "24 Hours", "24 Hours",
         "A+, B+, AB+, O+, B-, O-"),
        ("Max Blood Bank", "1 Press Enclave Road, Saket",
         "Delhi", "+91-11-26515050", 10.3, 1, "24 Hours", "24 Hours",
         "All Blood Groups"),
        ("Rotary Blood Bank", "Kailash Colony, Greater Kailash",
         "Delhi", "+91-11-29247977", 12.1, 0, "9:30 AM", "7:00 PM",
         "A+, B+, O+, AB+"),
    ]
    
    p = ph()
    for b in banks:
        cursor.execute(f"""
            INSERT INTO blood_banks 
            (name, address, city, phone, distance_km, is_open, 
             opening_time, closing_time, blood_groups)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
        """, b)
    
    conn.commit()
    conn.close()
    print(f"✅ {len(banks)} blood banks add ho gaye!")


def add_sample_checkup_centers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM checkup_centers")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    centers = [
        ("City Diagnostic Center", "45 Karol Bagh Main Road",
         "Delhi", "+91-11-28751234", 3.2, 1, "8:00 AM", "8:00 PM",
         "Blood Test, X-Ray, ECG, Ultrasound", "₹200 - ₹2000"),
        ("Apollo Diagnostics", "Sarita Vihar, Mathura Road",
         "Delhi", "+91-11-26925858", 8.5, 1, "7:00 AM", "10:00 PM",
         "Blood Test, X-Ray, ECG, MRI, CT Scan, Ultrasound", "₹300 - ₹8000"),
        ("Dr. Lal PathLabs", "Sector 18, Noida",
         "Noida", "+91-11-39885050", 15.2, 1, "6:30 AM", "9:00 PM",
         "Blood Test, Urine Test, ECG, Thyroid", "₹150 - ₹1500"),
        ("Metropolis Healthcare", "Andheri West, Mumbai",
         "Mumbai", "+91-22-33995000", 1200.0, 1, "7:00 AM", "9:00 PM",
         "Blood Test, X-Ray, ECG, MRI, CT Scan", "₹250 - ₹7000"),
        ("Healthians Diagnostic", "Connaught Place",
         "Delhi", "+91-11-41171000", 4.5, 1, "6:00 AM", "10:00 PM",
         "Blood Test, Urine Test, ECG", "₹199 - ₹2500"),
    ]
    
    p = ph()
    for c in centers:
        cursor.execute(f"""
            INSERT INTO checkup_centers 
            (name, address, city, phone, distance_km, is_open, 
             opening_time, closing_time, checkups, price_range)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
        """, c)
    
    conn.commit()
    conn.close()
    print(f"✅ {len(centers)} checkup centers add ho gaye!")


def add_sample_medical_stores():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM medical_stores")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    stores = [
        ("Jan Aushadhi Store", "Karol Bagh, Near Metro Station",
         "Delhi", "+91-11-28751111", 1.2, 1, "9:00 AM", "9:00 PM",
         "Generic Medicines, Ayurvedic, Surgical Items"),
        ("Apollo Pharmacy", "Sarita Vihar, Mathura Road",
         "Delhi", "+91-11-26925858", 8.5, 1, "24 Hours", "24 Hours",
         "All Medicines, Home Delivery, Health Products"),
        ("MedPlus Pharmacy", "Connaught Place, Block A",
         "Delhi", "+91-11-41171000", 4.5, 1, "8:00 AM", "11:00 PM",
         "Branded Medicines, Baby Care, Wellness Products"),
        ("Netmeds Store", "Nehru Place, Outer Ring Road",
         "Delhi", "+91-11-39885050", 12.0, 1, "9:00 AM", "10:00 PM",
         "Medicines, Health Devices, Home Delivery"),
        ("Wellness Forever", "Saket, Near Select City Walk",
         "Delhi", "+91-11-26515050", 10.3, 1, "24 Hours", "24 Hours",
         "All Medicines, Cosmetics, Health Drinks"),
        ("Local Medical Store", "Karol Bagh Main Market",
         "Delhi", "+91-98XXXXXXXX", 2.0, 1, "9:00 AM", "10:00 PM",
         "General Medicines, First Aid"),
    ]
    
    p = ph()
    for s in stores:
        cursor.execute(f"""
            INSERT INTO medical_stores 
            (name, address, city, phone, distance_km, is_open, 
             opening_time, closing_time, services)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
        """, s)
    
    conn.commit()
    conn.close()
    print(f"✅ {len(stores)} medical stores add ho gaye!")


def update_tokens_for_existing():
    """Jo doctors ke token missing hain unke liye token generate karo"""
    conn = get_connection()
    cursor = conn.cursor()
    p = ph()
    cursor.execute(f"SELECT id FROM doctors WHERE token IS NULL OR token = ''")
    doctors = cursor.fetchall()
    
    if not doctors:
        conn.close()
        return
    
    for (doc_id,) in doctors:
        token = generate_token()
        cursor.execute(f"UPDATE doctors SET token = {p} WHERE id = {p}", (token, doc_id))
    
    conn.commit()
    conn.close()
    print(f"✅ {len(doctors)} tokens update ho gaye!")


def show_all():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM doctors")
    d = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM blood_banks")
    b = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM checkup_centers")
    c = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM medical_stores")
    m = cursor.fetchone()[0]
    conn.close()
    print(f"\n📊 Doctors: {d}")
    print(f"📊 Blood Banks: {b}")
    print(f"📊 Checkup Centers: {c}")
    print(f"📊 Medical Stores: {m}")


if __name__ == "__main__":
    print("🚀 Database setup shuru...")
    print(f"🌐 Mode: {'PostgreSQL (Cloud)' if DATABASE_URL else 'SQLite (Local)'}\n")
    
    create_database()
    add_sample_doctors()
    add_sample_blood_banks()
    add_sample_checkup_centers()
    add_sample_medical_stores()
    update_tokens_for_existing()
    show_all()
    
    print("\n✅ Sab kuch ready hai!")