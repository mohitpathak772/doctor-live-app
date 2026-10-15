# ============================================
# qr_system.py
# QR Code generate (GPS coordinates ke saath)
# ============================================

import qrcode
import os
import socket
from database import get_connection, ph

QR_FOLDER = "qr_codes"


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def get_base_url():
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if render_url:
        return render_url
    return f"http://{get_local_ip()}:5000"


def ensure_qr_folder():
    if not os.path.exists(QR_FOLDER):
        os.makedirs(QR_FOLDER)


def generate_qr_for_doctor(doctor_id, doctor_name, doctor_token):
    """Doctor ke liye QR banata hai - token ke saath"""
    ensure_qr_folder()
    
    base_url = get_base_url()
    qr_data = f"{base_url}/doctor/{doctor_id}?token={doctor_token}"
    
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
    print(f"   🔐 Token: {doctor_token[:10]}...")
    return file_path


def generate_qr_for_all_doctors():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, token FROM doctors ORDER BY id")
    doctors = cursor.fetchall()
    conn.close()
    
    if not doctors:
        print("❌ Koi doctor nahi mila.")
        return
    
    print("\n" + "=" * 70)
    print("📸 QR CODES GENERATE HO RAHE HAIN")
    print(f"🌐 Base URL: {get_base_url()}")
    print("=" * 70 + "\n")
    
    for doc_id, name, token in doctors:
        if not token:
            print(f"⚠️  Doctor {doc_id} ({name}) ka token nahi hai.")
            continue
        generate_qr_for_doctor(doc_id, name, token)
    
    print(f"\n✅ Saare QR codes '{QR_FOLDER}' mein save ho gaye!")


if __name__ == "__main__":
    generate_qr_for_all_doctors()