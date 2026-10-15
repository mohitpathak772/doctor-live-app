# ============================================
# qr_render.py
# Render URL ke saath QR generate karta hai
# (GPS HTTPS pe kaam karega)
# ============================================

import qrcode
import os
from database import get_connection

QR_FOLDER = "qr_codes_render"

# ⚠️ APNA RENDER URL YAHAN DAALEIN
RENDER_URL = "https://doctor-live-app.onrender.com"


def ensure_folder():
    if not os.path.exists(QR_FOLDER):
        os.makedirs(QR_FOLDER)


def generate_all():
    ensure_folder()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, token FROM doctors ORDER BY id")
    doctors = cursor.fetchall()
    conn.close()
    
    if not doctors:
        print("❌ Koi doctor nahi mila.")
        return
    
    print(f"\n📸 Render URL ke saath QR codes ban rahe hain...")
    print(f"🌐 Base URL: {RENDER_URL}\n")
    print("=" * 70)
    
    for doc_id, name, token in doctors:
        if not token:
            print(f"⚠️  Doctor {doc_id} ka token nahi hai. Skip.")
            continue
        
        qr_data = f"{RENDER_URL}/doctor/{doc_id}?token={token}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=12,
            border=3,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        safe_name = "".join(c if c.isalnum() else "_" for c in name)
        file_path = os.path.join(QR_FOLDER, f"{safe_name}_id{doc_id}.png")
        img.save(file_path)
        
        print(f"\n✅ {name}")
        print(f"   📱 {qr_data}")
    
    print("\n" + "=" * 70)
    print(f"\n✅ Saare QR codes '{QR_FOLDER}' mein save ho gaye!")
    print(f"\n💡 Ab in QR ko phone se scan karein — GPS chalega!")


if __name__ == "__main__":
    generate_all()