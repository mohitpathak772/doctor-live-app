# ============================================
# qr_system.py
# QR Code generate + scan
# SQLite (local) + PostgreSQL (cloud) dono support
# ============================================

import qrcode
import os
import socket
from datetime import datetime
from database import get_connection, ph

QR_FOLDER = "qr_codes"


# ============================================
# Helper Functions
# ============================================

def get_local_ip():
    """PC ka local IP nikalta hai"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def get_base_url():
    """Server ka base URL deta hai (Render ya local)"""
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if render_url:
        return render_url
    return f"http://{get_local_ip()}:5000"


def ensure_qr_folder():
    """QR folder banata hai (agar nahi hai)"""
    if not os.path.exists(QR_FOLDER):
        os.makedirs(QR_FOLDER)


# ============================================
# QR Generate
# ============================================

def generate_qr_for_doctor(doctor_id, doctor_name):
    """Doctor ke liye QR banata hai (URL ke saath)"""
    ensure_qr_folder()
    
    base_url = get_base_url()
    qr_data = f"{base_url}/doctor/{doctor_id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=3,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    safe_name = "".join(c if c.isalnum() else "_" for c in doctor_name)
    file_path = os.path.join(QR_FOLDER, f"{safe_name}_id{doctor_id}.png")
    img.save(file_path)
    
    print(f"✅ QR: {file_path}")
    print(f"   📱 URL: {qr_data}")
    return file_path


def generate_qr_for_all_doctors():
    """Saare doctors ke QR banata hai"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM doctors ORDER BY id")
    doctors = cursor.fetchall()
    conn.close()
    
    if not doctors:
        print("❌ Koi doctor nahi mila.")
        return
    
    print("\n" + "=" * 60)
    print("📸 QR CODES GENERATE HO RAHE HAIN")
    print(f"🌐 Base URL: {get_base_url()}")
    print("=" * 60 + "\n")
    
    for doc_id, name in doctors:
        generate_qr_for_doctor(doc_id, name)
    
    print(f"\n✅ Saare QR codes '{QR_FOLDER}' mein save ho gaye!")


# ============================================
# Scan / Status Update
# ============================================

def scan_qr(qr_data):
    """QR data se doctor ID nikaal kar present karta hai"""
    
    # URL se ID nikaalo
    if "/doctor/" in qr_data:
        try:
            doctor_id = int(qr_data.split("/doctor/")[-1].split("/")[0].split("?")[0])
        except ValueError:
            return False, "❌ QR data mein gadbad hai!"
    elif qr_data.startswith("DOCTOR-"):
        try:
            doctor_id = int(qr_data.replace("DOCTOR-", ""))
        except ValueError:
            return False, "❌ QR data mein gadbad hai!"
    elif qr_data.isdigit():
        doctor_id = int(qr_data)
    else:
        return False, "❌ Ye valid Doctor QR nahi hai!"
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT name, hospital_name FROM doctors WHERE id = {ph()}",
        (doctor_id,)
    )
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return False, f"❌ Doctor ID {doctor_id} nahi mila!"
    
    doctor_name, hospital = result
    
    cursor.execute(
        f"UPDATE doctors SET is_present = 1 WHERE id = {ph()}",
        (doctor_id,)
    )
    conn.commit()
    conn.close()
    
    current_time = datetime.now().strftime("%I:%M %p")
    message = f"✅ {doctor_name} ab PRESENT hain ({current_time})"
    print(message)
    return True, message


def mark_absent(doctor_id):
    """Doctor ko absent karta hai"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT name FROM doctors WHERE id = {ph()}",
        (doctor_id,)
    )
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return False, "❌ Doctor nahi mila!"
    
    doctor_name = result[0]
    cursor.execute(
        f"UPDATE doctors SET is_present = 0 WHERE id = {ph()}",
        (doctor_id,)
    )
    conn.commit()
    conn.close()
    
    message = f"🔴 {doctor_name} ab ABSENT hain"
    print(message)
    return True, message


# ============================================
# Testing
# ============================================

if __name__ == "__main__":
    print("🎯 QR System Test\n")
    generate_qr_for_all_doctors()
    print("\n✅ Test complete!")