# ============================================
# migrate_db.py
# Purane database mein naye columns add karta hai
# Ek baar chalayein, phir delete kar dein
# ============================================

from database import get_connection, ph, generate_token

def migrate():
    conn = get_connection()
    cursor = conn.cursor()
    p = ph()
    
    print("🔍 Migration shuru...")
    
    # Check karo: token column hai ya nahi
    try:
        cursor.execute("SELECT token FROM doctors LIMIT 1")
        print("✅ token column already exists!")
    except Exception as e:
        print(f"⚠️ token column missing. Add kar rahe hain...")
        try:
            cursor.execute("ALTER TABLE doctors ADD COLUMN token TEXT")
            print("✅ token column add ho gaya!")
        except Exception as e2:
            print(f"❌ Error: {e2}")
    
    # Check karo: hospital_lat column
    try:
        cursor.execute("SELECT hospital_lat FROM doctors LIMIT 1")
        print("✅ hospital_lat column already exists!")
    except Exception:
        print("⚠️ hospital_lat column missing. Add kar rahe hain...")
        try:
            cursor.execute("ALTER TABLE doctors ADD COLUMN hospital_lat REAL")
            print("✅ hospital_lat column add ho gaya!")
        except Exception as e2:
            print(f"❌ Error: {e2}")
    
    # Check karo: hospital_lng column
    try:
        cursor.execute("SELECT hospital_lng FROM doctors LIMIT 1")
        print("✅ hospital_lng column already exists!")
    except Exception:
        print("⚠️ hospital_lng column missing. Add kar rahe hain...")
        try:
            cursor.execute("ALTER TABLE doctors ADD COLUMN hospital_lng REAL")
            print("✅ hospital_lng column add ho gaya!")
        except Exception as e2:
            print(f"❌ Error: {e2}")
    
    # Check karo: users table
    try:
        cursor.execute("SELECT id FROM users LIMIT 1")
        print("✅ users table exists!")
    except Exception:
        print("⚠️ users table missing. Bana rahe hain...")
        try:
            if p == "%s":
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
            print("✅ users + otps tables ban gayi!")
        except Exception as e2:
            print(f"❌ Error: {e2}")
    
    # Ab saare doctors ke liye token generate karo (agar missing hai)
    cursor.execute(f"SELECT id FROM doctors WHERE token IS NULL OR token = ''")
    missing = cursor.fetchall()
    
    if missing:
        print(f"\n📝 {len(missing)} doctors ke liye token generate kar rahe hain...")
        for (doc_id,) in missing:
            token = generate_token()
            cursor.execute(
                f"UPDATE doctors SET token = {p} WHERE id = {p}",
                (token, doc_id)
            )
        print(f"✅ {len(missing)} tokens generate ho gaye!")
    else:
        print("✅ Saare doctors ke tokens already hain!")
    
    conn.commit()
    conn.close()
    print("\n🎉 Migration complete!")

if __name__ == "__main__":
    migrate()