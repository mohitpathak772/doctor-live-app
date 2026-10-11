# ============================================
# poster_generator.py
# Doctor ke liye printable poster banata hai
# ============================================

import qrcode
from PIL import Image, ImageDraw, ImageFont
import sqlite3
import os
import socket

DB_NAME = "doctors.db"
QR_FOLDER = "qr_codes"
POSTER_FOLDER = "posters"


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


def ensure_folders():
    """Zaroori folders banata hai"""
    for folder in [QR_FOLDER, POSTER_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)


def generate_qr_image(doctor_id, server_ip):
    """Sirf QR image banata hai (bade size ka)"""
    qr_data = f"http://{server_ip}:5000/doctor/{doctor_id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=15,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Temporary QR file
    temp_qr_path = os.path.join(QR_FOLDER, f"temp_qr_{doctor_id}.png")
    img.save(temp_qr_path)
    
    return temp_qr_path, qr_data


def get_font(size, bold=False):
    """Font load karta hai (Windows ke liye)"""
    try:
        if bold:
            return ImageFont.truetype("arialbd.ttf", size)
        else:
            return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()


def create_poster(doctor_id, name, spec, degree, hospital, htype, city, server_ip):
    """Ek doctor ka printable poster banata hai"""
    
    # Poster size (A4 = 2480 x 3508 pixels at 300 DPI)
    # Lekin hum thoda chhota rakhenge - 1200 x 1600 (accha quality)
    WIDTH = 1200
    HEIGHT = 1600
    
    # White background
    poster = Image.new('RGB', (WIDTH, HEIGHT), 'white')
    draw = ImageDraw.Draw(poster)
    
    # Colors
    DARK_BLUE = (30, 58, 138)
    LIGHT_BLUE = (59, 130, 246)
    GREEN = (34, 197, 94)
    GRAY = (100, 116, 139)
    LIGHT_GRAY = (241, 245, 249)
    
    # === TOP HEADER (blue bar) ===
    draw.rectangle([(0, 0), (WIDTH, 180)], fill=DARK_BLUE)
    
    # Hospital name / Title
    title_font = get_font(60, bold=True)
    draw.text((WIDTH // 2, 60), "🏥 DOCTOR LIVE", 
              fill='white', font=title_font, anchor="mm")
    
    subtitle_font = get_font(28)
    draw.text((WIDTH // 2, 130), "Scan karein - Doctor ka status janein", 
              fill=(203, 213, 225), font=subtitle_font, anchor="mm")
    
    # === DOCTOR INFO SECTION ===
    # Background for doctor info
    draw.rectangle([(40, 220), (WIDTH - 40, 580)], fill=LIGHT_GRAY, outline=DARK_BLUE, width=3)
    
    # Doctor icon + name
    name_font = get_font(52, bold=True)
    draw.text((WIDTH // 2, 290), f"👨‍⚕️ {name}", 
              fill=DARK_BLUE, font=name_font, anchor="mm")
    
    # Degree + Specialization
    spec_font = get_font(36)
    draw.text((WIDTH // 2, 370), f"{degree}", 
              fill=GRAY, font=spec_font, anchor="mm")
    
    draw.text((WIDTH // 2, 420), f"{spec}", 
              fill=LIGHT_BLUE, font=spec_font, anchor="mm")
    
    # Hospital
    hosp_font = get_font(32)
    hosp_icon = "🏛️" if htype == "Government" else "🏥"
    draw.text((WIDTH // 2, 490), f"{hosp_icon} {hospital}", 
              fill=GRAY, font=hosp_font, anchor="mm")
    
    # City
    draw.text((WIDTH // 2, 540), f"📍 {city}", 
              fill=GRAY, font=get_font(28), anchor="mm")
    
    # === QR CODE SECTION ===
    qr_label_font = get_font(38, bold=True)
    draw.text((WIDTH // 2, 650), "📱 YAHAN SCAN KAREIN", 
              fill=DARK_BLUE, font=qr_label_font, anchor="mm")
    
    # QR Code banao aur paste karo
    qr_path, qr_url = generate_qr_image(doctor_id, server_ip)
    qr_img = Image.open(qr_path)
    
    # QR ka size (square)
    QR_SIZE = 500
    qr_img = qr_img.resize((QR_SIZE, QR_SIZE), Image.LANCZOS)
    
    # QR position (center)
    qr_x = (WIDTH - QR_SIZE) // 2
    qr_y = 700
    
    # QR ke around border
    draw.rectangle(
        [(qr_x - 15, qr_y - 15), (qr_x + QR_SIZE + 15, qr_y + QR_SIZE + 15)],
        outline=DARK_BLUE, width=5
    )
    
    poster.paste(qr_img, (qr_x, qr_y))
    
    # === INSTRUCTIONS ===
    instruction_y = qr_y + QR_SIZE + 80
    
    # Big instruction
    big_font = get_font(38, bold=True)
    draw.text((WIDTH // 2, instruction_y), 
              "🚀 3 AASAN STEPS", 
              fill=GREEN, font=big_font, anchor="mm")
    
    # Steps
    step_font = get_font(28)
    steps = [
        "1. Phone ka camera kholo",
        "2. Ye QR code scan karo", 
        "3. 'Mark Present' button dabao"
    ]
    
    for i, step in enumerate(steps):
        y = instruction_y + 60 + (i * 45)
        draw.text((WIDTH // 2, y), step, 
                  fill=GRAY, font=step_font, anchor="mm")
    
    # === FOOTER ===
    draw.rectangle([(0, HEIGHT - 100), (WIDTH, HEIGHT)], fill=DARK_BLUE)
    footer_font = get_font(24)
    draw.text((WIDTH // 2, HEIGHT - 50), 
              "Powered by Doctor Live | Patient ke liye behtar seva", 
              fill=(203, 213, 225), font=footer_font, anchor="mm")
    
    # === Save ===
    safe_name = "".join(c if c.isalnum() else "_" for c in name)
    poster_path = os.path.join(POSTER_FOLDER, f"Poster_{safe_name}_id{doctor_id}.png")
    poster.save(poster_path, "PNG", quality=95)
    
    # Temp QR delete karo
    try:
        os.remove(qr_path)
    except:
        pass
    
    return poster_path


def generate_posters_for_all():
    """Saare doctors ke posters banata hai"""
    
    ensure_folders()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, specialization, degree, hospital_name, 
               hospital_type, city
        FROM doctors ORDER BY id
    """)
    doctors = cursor.fetchall()
    conn.close()
    
    if not doctors:
        print("❌ Koi doctor nahi mila!")
        return
    
    server_ip = get_local_ip()
    
    print("\n" + "=" * 60)
    print("📄 POSTERS BAN RAHE HAIN...")
    print(f"🌐 Server IP: {server_ip}")
    print("=" * 60 + "\n")
    
    for doc in doctors:
        doc_id, name, spec, degree, hosp, htype, city = doc
        
        poster_path = create_poster(
            doc_id, name, spec, degree, hosp, htype, city, server_ip
        )
        
        print(f"✅ Poster ban gaya: {poster_path}")
    
    print(f"\n🎉 Saare posters '{POSTER_FOLDER}' folder mein save ho gaye!")
    print(f"💡 Ab inhe print karke doctor ke office mein lagayein!")


if __name__ == "__main__":
    generate_posters_for_all()