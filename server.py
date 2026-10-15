# ============================================
# server.py - Doctor Live Complete App
# Part 1: Imports + Helpers + Login + Language
# ============================================

from flask import Flask, render_template_string, request, redirect, session, url_for, send_file
import socket
import os
import io
from datetime import datetime, timedelta
from database import (get_connection, ph, create_database,
                      add_sample_doctors, add_sample_blood_banks,
                      add_sample_checkup_centers, add_sample_medical_stores,
                      update_tokens_for_existing, generate_otp,
                      generate_token, DATABASE_URL)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "doctor-live-secret-key-2024")


# ============================================
# AUTO MIGRATION (Render ke purane database ke liye)
# ============================================

def auto_migrate():
    columns_to_add = [
        ("token", "TEXT"),
        ("hospital_lat", "REAL"),
        ("hospital_lng", "REAL"),
    ]
    for col_name, col_type in columns_to_add:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(f"SELECT {col_name} FROM doctors LIMIT 1")
                conn.close()
                print(f"✅ {col_name} already exists")
                continue
            except Exception:
                try:
                    conn.rollback()
                except:
                    pass
                conn.close()
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(f"ALTER TABLE doctors ADD COLUMN {col_name} {col_type}")
                conn.commit()
                conn.close()
                print(f"✅ {col_name} column added")
        except Exception as e:
            print(f"⚠️ Error adding {col_name}: {e}")

auto_migrate()


# ============================================
# Initialize Database
# ============================================

try:
    print("🚀 Database initialize ho raha hai...")
    create_database()
    add_sample_doctors()
    add_sample_blood_banks()
    add_sample_checkup_centers()
    add_sample_medical_stores()
    update_tokens_for_existing()
    print("✅ Database ready!")
except Exception as e:
    print(f"⚠️ Database init error: {e}")


# ============================================
# Helper Functions
# ============================================

def get_doctor(doctor_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id, name, specialization, degree, hospital_name, 
               hospital_type, city, medicines, is_present, token,
               hospital_lat, hospital_lng
        FROM doctors WHERE id = {ph()}
    """, (doctor_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def get_all_doctors():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, specialization, degree, hospital_name, 
               hospital_type, city, medicines, is_present
        FROM doctors ORDER BY hospital_type, name
    """)
    result = cursor.fetchall()
    conn.close()
    return result


def get_all_blood_banks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, address, city, phone, distance_km,
               is_open, opening_time, closing_time, blood_groups
        FROM blood_banks ORDER BY distance_km
    """)
    result = cursor.fetchall()
    conn.close()
    return result


def get_all_checkup_centers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, address, city, phone, distance_km,
               is_open, opening_time, closing_time, checkups, price_range
        FROM checkup_centers ORDER BY distance_km
    """)
    result = cursor.fetchall()
    conn.close()
    return result


def get_all_medical_stores():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, address, city, phone, distance_km,
               is_open, opening_time, closing_time, services
        FROM medical_stores ORDER BY distance_km
    """)
    result = cursor.fetchall()
    conn.close()
    return result


def set_doctor_status(doctor_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE doctors SET is_present = {ph()} WHERE id = {ph()}",
        (status, doctor_id)
    )
    conn.commit()
    conn.close()


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


def save_otp(mobile, otp):
    conn = get_connection()
    cursor = conn.cursor()
    p = ph()
    cursor.execute(f"DELETE FROM otps WHERE mobile = {p}", (mobile,))
    cursor.execute(f"""
        INSERT INTO otps (mobile, otp, created_at)
        VALUES ({p}, {p}, {p})
    """, (mobile, otp, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def verify_otp(mobile, otp):
    conn = get_connection()
    cursor = conn.cursor()
    p = ph()
    cursor.execute(f"""
        SELECT id, created_at FROM otps 
        WHERE mobile = {p} AND otp = {p}
    """, (mobile, otp))
    result = cursor.fetchone()
    conn.close()
    if not result:
        return False
    try:
        created = datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S")
        if datetime.now() - created > timedelta(minutes=10):
            return False
    except:
        pass
    return True


def get_or_create_user(mobile):
    conn = get_connection()
    cursor = conn.cursor()
    p = ph()
    cursor.execute(f"SELECT id, language FROM users WHERE mobile = {p}", (mobile,))
    user = cursor.fetchone()
    if not user:
        cursor.execute(f"""
            INSERT INTO users (mobile, language, created_at)
            VALUES ({p}, {p}, {p})
        """, (mobile, "hi", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        cursor.execute(f"SELECT id, language FROM users WHERE mobile = {p}", (mobile,))
        user = cursor.fetchone()
    conn.close()
    return user


def update_user_language(mobile, language):
    conn = get_connection()
    cursor = conn.cursor()
    p = ph()
    cursor.execute(f"UPDATE users SET language = {p} WHERE mobile = {p}", (language, mobile))
    conn.commit()
    conn.close()


# ============================================
# Translations
# ============================================

TRANSLATIONS = {
    "hi": {"app_name": "🏥 डॉक्टर लाइव", "tagline": "डॉक्टर की उपलब्धता देखें",
        "mobile_label": "📱 मोबाइल नंबर", "send_otp": "OTP भेजें",
        "otp_label": "OTP डालें", "verify": "वेरिफाई करें",
        "doctors": "डॉक्टर", "blood_banks": "ब्लड बैंक", "checkup": "चेकअप",
        "medical": "मेडिकल", "govt": "🏛️ सरकारी", "private": "🏥 प्राइवेट",
        "present": "🟢 मौजूद", "absent": "🔴 नहीं है", "speak": "🔊 सुनें",
        "open": "🟢 खुला", "closed": "🔴 बंद", "km_away": "किमी दूर",
        "call": "📞 कॉल", "search": "🔍 खोजें...", "no_results": "😕 कुछ नहीं मिला",
        "logout": "लॉग आउट", "speak_all": "🔊 सब सुनें"},
    "en": {"app_name": "🏥 Doctor Live", "tagline": "Check doctor availability",
        "mobile_label": "📱 Mobile Number", "send_otp": "Send OTP",
        "otp_label": "Enter OTP", "verify": "Verify",
        "doctors": "Doctors", "blood_banks": "Blood Banks", "checkup": "Checkup",
        "medical": "Medical", "govt": "🏛️ Government", "private": "🏥 Private",
        "present": "🟢 Present", "absent": "🔴 Absent", "speak": "🔊 Speak",
        "open": "🟢 Open", "closed": "🔴 Closed", "km_away": "km away",
        "call": "📞 Call", "search": "🔍 Search...", "no_results": "😕 No results",
        "logout": "Logout", "speak_all": "🔊 Speak All"}
}
for _l in ["bn", "ta", "te", "mr", "gu", "kn", "ml", "pa"]:
    TRANSLATIONS[_l] = TRANSLATIONS["en"].copy()


def t(key, lang="hi"):
    return TRANSLATIONS.get(lang, TRANSLATIONS["hi"]).get(key, key)
# ============================================
# LOGIN PAGE
# ============================================

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Doctor Live - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .container { background: white; padding: 40px 30px; border-radius: 20px; max-width: 420px; width: 100%; }
        .logo { text-align: center; font-size: 60px; margin-bottom: 10px; }
        h1 { text-align: center; color: #1e3a8a; font-size: 26px; margin-bottom: 8px; }
        .tagline { text-align: center; color: #64748b; font-size: 13px; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-weight: bold; color: #1e293b; font-size: 14px; margin-bottom: 8px; }
        input { width: 100%; padding: 14px; border: 2px solid #cbd5e1; border-radius: 10px; font-size: 15px; outline: none; }
        .btn { width: 100%; padding: 16px; background: #1e3a8a; color: white; border: none; border-radius: 10px; font-size: 15px; font-weight: bold; cursor: pointer; }
        .demo-otp { background: #fef3c7; border: 2px solid #f59e0b; padding: 12px; border-radius: 10px; text-align: center; margin: 15px 0; font-size: 13px; color: #78350f; }
        .demo-otp strong { font-size: 20px; color: #92400e; letter-spacing: 4px; }
        .error { background: #fee2e2; color: #991b1b; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 15px; text-align: center; }
        .success { background: #dcfce7; color: #166534; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 15px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🏥</div>
        <h1>{{ app_name }}</h1>
        <p class="tagline">{{ tagline }}</p>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        {% if step == 'mobile' %}
        <form method="POST">
            <div class="form-group">
                <label>{{ mobile_label }}</label>
                <input type="tel" name="mobile" placeholder="9876543210" pattern="[0-9]{10}" maxlength="10" required autofocus>
            </div>
            <button type="submit" class="btn">{{ send_otp }} →</button>
        </form>
        {% elif step == 'otp' %}
        <div class="success">✅ OTP bhej diya: +91{{ mobile }}</div>
        <div class="demo-otp">💡 Demo OTP: <strong>{{ demo_otp }}</strong></div>
        <form method="POST">
            <input type="hidden" name="mobile" value="{{ mobile }}">
            <div class="form-group">
                <label>{{ otp_label }}</label>
                <input type="text" name="otp" placeholder="______" pattern="[0-9]{6}" maxlength="6" required autofocus>
            </div>
            <button type="submit" class="btn">{{ verify }} ✅</button>
        </form>
        {% endif %}
    </div>
</body>
</html>
"""


# ============================================
# LANGUAGE PAGE
# ============================================

LANGUAGE_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Select Language</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); min-height: 100vh; padding: 20px; display: flex; align-items: center; justify-content: center; }
        .container { background: white; padding: 30px 25px; border-radius: 20px; max-width: 450px; width: 100%; }
        h1 { text-align: center; color: #1e3a8a; font-size: 22px; margin-bottom: 25px; }
        .lang-list { display: grid; gap: 10px; margin-bottom: 25px; }
        .lang-item { display: flex; align-items: center; padding: 15px; border: 2px solid #cbd5e1; border-radius: 12px; cursor: pointer; background: white; }
        .lang-item:hover { border-color: #3b82f6; background: #eff6ff; }
        .lang-item input { margin-right: 12px; transform: scale(1.3); }
        .lang-item label { cursor: pointer; font-size: 15px; font-weight: 500; flex: 1; }
        .btn { width: 100%; padding: 16px; background: #1e3a8a; color: white; border: none; border-radius: 10px; font-size: 16px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 भाषा चुनें / Select Language</h1>
        <form method="POST">
            <div class="lang-list">
                <div class="lang-item" onclick="document.getElementById('hi').checked=true"><input type="radio" name="language" value="hi" id="hi" checked><label for="hi">हिंदी (Hindi)</label></div>
                <div class="lang-item" onclick="document.getElementById('en').checked=true"><input type="radio" name="language" value="en" id="en"><label for="en">English</label></div>
                <div class="lang-item" onclick="document.getElementById('bn').checked=true"><input type="radio" name="language" value="bn" id="bn"><label for="bn">বাংলা (Bengali)</label></div>
                <div class="lang-item" onclick="document.getElementById('ta').checked=true"><input type="radio" name="language" value="ta" id="ta"><label for="ta">தமிழ் (Tamil)</label></div>
                <div class="lang-item" onclick="document.getElementById('te').checked=true"><input type="radio" name="language" value="te" id="te"><label for="te">తెలుగు (Telugu)</label></div>
                <div class="lang-item" onclick="document.getElementById('mr').checked=true"><input type="radio" name="language" value="mr" id="mr"><label for="mr">मराठी (Marathi)</label></div>
                <div class="lang-item" onclick="document.getElementById('gu').checked=true"><input type="radio" name="language" value="gu" id="gu"><label for="gu">ગુજરાતી (Gujarati)</label></div>
                <div class="lang-item" onclick="document.getElementById('kn').checked=true"><input type="radio" name="language" value="kn" id="kn"><label for="kn">ಕನ್ನಡ (Kannada)</label></div>
                <div class="lang-item" onclick="document.getElementById('ml').checked=true"><input type="radio" name="language" value="ml" id="ml"><label for="ml">മലയാളം (Malayalam)</label></div>
                <div class="lang-item" onclick="document.getElementById('pa').checked=true"><input type="radio" name="language" value="pa" id="pa"><label for="pa">ਪੰਜਾਬੀ (Punjabi)</label></div>
            </div>
            <button type="submit" class="btn">आगे बढ़ें / Proceed →</button>
        </form>
    </div>
</body>
</html>
"""


# ============================================
# HOME PAGE
# ============================================

HOME_PAGE = """
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t.app_name }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f4f8; padding: 12px; }
        .header { background: #1e3a8a; color: white; padding: 14px 16px; border-radius: 10px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
        .header-left h1 { font-size: 20px; }
        .header-left p { font-size: 11px; color: #cbd5e1; margin-top: 3px; }
        .header-right { display: flex; gap: 8px; align-items: center; }
        .header-right select { padding: 5px 8px; border-radius: 6px; border: none; font-size: 12px; }
        .logout-btn { background: #dc2626; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: bold; }
        .tabs { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px; }
        .tab { background: white; padding: 14px 8px; border-radius: 10px; text-align: center; cursor: pointer; font-size: 12px; font-weight: bold; color: #475569; text-decoration: none; border: 2px solid transparent; }
        .tab.active { background: #1e3a8a; color: white; }
        .tab .icon { font-size: 22px; display: block; margin-bottom: 4px; }
        .tab.blood.active { background: #dc2626; }
        .tab.checkup.active { background: #059669; }
        .tab.medical.active { background: #7c3aed; }
        .tools { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
        .search-box { flex: 1; min-width: 200px; padding: 12px 14px; border: 2px solid #cbd5e1; border-radius: 10px; font-size: 14px; }
        .voice-btn { background: #7c3aed; color: white; padding: 12px 16px; border: none; border-radius: 10px; font-size: 13px; font-weight: bold; cursor: pointer; }
        .section-header { background: #fef3c7; color: #92400e; padding: 10px 14px; border-radius: 8px; font-weight: bold; font-size: 14px; margin: 15px 0 10px 0; }
        .section-header.private { background: #dbeafe; color: #1e40af; }
        .section-header.blood { background: #fee2e2; color: #991b1b; }
        .section-header.checkup { background: #d1fae5; color: #065f46; }
        .section-header.medical { background: #ede9fe; color: #5b21b6; }
        .card { background: white; padding: 14px; border-radius: 10px; border-left: 5px solid #ef4444; margin-bottom: 10px; }
        .card.present { border-left-color: #22c55e; }
        .card.govt { border-left-color: #f59e0b; }
        .card.blood { border-left-color: #dc2626; }
        .card.checkup { border-left-color: #059669; }
        .card.medical { border-left-color: #7c3aed; }
        .card-header { display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 8px; }
        .card-title { font-size: 16px; font-weight: bold; color: #1e293b; }
        .card-info { font-size: 13px; color: #64748b; margin-top: 3px; }
        .card-distance { font-size: 12px; color: #7c3aed; font-weight: bold; margin-top: 5px; }
        .card-phone { font-size: 12px; color: #1e40af; margin-top: 4px; }
        .card-timing { font-size: 12px; color: #64748b; margin-top: 4px; }
        .card-badge { font-size: 11px; padding: 3px 10px; border-radius: 12px; font-weight: bold; display: inline-block; margin-top: 6px; margin-right: 4px; }
        .card-badge.present { background: #dcfce7; color: #166534; }
        .card-badge.absent { background: #fee2e2; color: #991b1b; }
        .card-badge.open { background: #dcfce7; color: #166534; }
        .card-badge.closed { background: #fee2e2; color: #991b1b; }
        .card-badge.medicines { background: #f3e8ff; color: #7c3aed; }
        .card-badge.groups { background: #fee2e2; color: #dc2626; }
        .card-actions { text-align: right; min-width: 100px; }
        .call-btn { display: inline-block; background: #22c55e; color: white; padding: 7px 14px; border-radius: 7px; text-decoration: none; font-size: 12px; font-weight: bold; margin-top: 6px; }
        .speak-btn { display: inline-block; background: #7c3aed; color: white; padding: 6px 12px; border-radius: 6px; font-size: 11px; font-weight: bold; border: none; cursor: pointer; margin-top: 6px; }
        .no-results { text-align: center; padding: 40px 20px; color: #64748b; font-size: 15px; }
        @media (max-width: 500px) {
            .header-left h1 { font-size: 17px; }
            .tab { padding: 10px 4px; font-size: 11px; }
            .tab .icon { font-size: 18px; }
        }
    </style>
</head>
<body>

<div class="header">
    <div class="header-left">
        <h1>{{ t.app_name }}</h1>
        <p>{{ t.tagline }}</p>
    </div>
    <div class="header-right">
        <select onchange="changeLanguage(this.value)">
            <option value="hi" {% if lang == 'hi' %}selected{% endif %}>हिंदी</option>
            <option value="en" {% if lang == 'en' %}selected{% endif %}>English</option>
            <option value="bn" {% if lang == 'bn' %}selected{% endif %}>বাংলা</option>
            <option value="ta" {% if lang == 'ta' %}selected{% endif %}>தமிழ்</option>
            <option value="te" {% if lang == 'te' %}selected{% endif %}>తెలుగు</option>
            <option value="mr" {% if lang == 'mr' %}selected{% endif %}>मराठी</option>
            <option value="gu" {% if lang == 'gu' %}selected{% endif %}>ગુજરાતી</option>
            <option value="kn" {% if lang == 'kn' %}selected{% endif %}>ಕನ್ನಡ</option>
            <option value="ml" {% if lang == 'ml' %}selected{% endif %}>മലയാളം</option>
            <option value="pa" {% if lang == 'pa' %}selected{% endif %}>ਪੰਜਾਬੀ</option>
        </select>
        <a href="/logout" class="logout-btn">{{ t.logout }}</a>
    </div>
</div>

<div class="tabs">
    <a href="/?tab=doctors&lang={{ lang }}" class="tab {% if tab == 'doctors' %}active{% endif %}">
        <span class="icon">👨‍⚕️</span>{{ t.doctors }}
    </a>
    <a href="/?tab=blood&lang={{ lang }}" class="tab blood {% if tab == 'blood' %}active{% endif %}">
        <span class="icon">🩸</span>{{ t.blood_banks }}
    </a>
    <a href="/?tab=checkup&lang={{ lang }}" class="tab checkup {% if tab == 'checkup' %}active{% endif %}">
        <span class="icon">🏥</span>{{ t.checkup }}
    </a>
    <a href="/?tab=medical&lang={{ lang }}" class="tab medical {% if tab == 'medical' %}active{% endif %}">
        <span class="icon">💊</span>{{ t.medical }}
    </a>
</div>

<div class="tools">
    <input type="text" class="search-box" id="searchBox" placeholder="{{ t.search }}" onkeyup="filterCards()">
    <button class="voice-btn" onclick="speakCurrentTab()">🔊 {{ t.speak_all }}</button>
</div>

{% if tab == 'doctors' %}
    {% if govt_doctors %}
    <div class="section-header">{{ t.govt }} — {{ govt_doctors|length }}</div>
    {% for doc in govt_doctors %}
    <div class="card govt {% if doc[8] %}present{% endif %}" data-search="{{ doc[1] }} {{ doc[2] }} {{ doc[4] }}">
        <div class="card-header">
            <div style="flex: 1;">
                <div class="card-title">👨‍⚕️ {{ doc[1] }}</div>
                <div class="card-info">🎓 {{ doc[3] }} — {{ doc[2] }}</div>
                <div class="card-info">🏥 {{ doc[4] }}</div>
                <div class="card-info">📍 {{ doc[6] }}</div>
                {% if doc[7] %}<div class="card-badge medicines">💊 {{ doc[7] }}</div>{% endif %}
            </div>
            <div class="card-actions">
                <div class="card-badge {% if doc[8] %}present{% else %}absent{% endif %}">
                    {% if doc[8] %}{{ t.present }}{% else %}{{ t.absent }}{% endif %}
                </div><br>
                <button class="speak-btn" onclick="speakDoctor('{{ doc[1] }}', '{{ doc[4] }}', {{ 'true' if doc[8] else 'false' }})">{{ t.speak }}</button>
            </div>
        </div>
    </div>
    {% endfor %}
    {% endif %}
    
    {% if pvt_doctors %}
    <div class="section-header private">{{ t.private }} — {{ pvt_doctors|length }}</div>
    {% for doc in pvt_doctors %}
    <div class="card {% if doc[8] %}present{% endif %}" data-search="{{ doc[1] }} {{ doc[2] }} {{ doc[4] }}">
        <div class="card-header">
            <div style="flex: 1;">
                <div class="card-title">👨‍⚕️ {{ doc[1] }}</div>
                <div class="card-info">🎓 {{ doc[3] }} — {{ doc[2] }}</div>
                <div class="card-info">🏥 {{ doc[4] }}</div>
                <div class="card-info">📍 {{ doc[6] }}</div>
                {% if doc[7] %}<div class="card-badge medicines">💊 {{ doc[7] }}</div>{% endif %}
            </div>
            <div class="card-actions">
                <div class="card-badge {% if doc[8] %}present{% else %}absent{% endif %}">
                    {% if doc[8] %}{{ t.present }}{% else %}{{ t.absent }}{% endif %}
                </div><br>
                <button class="speak-btn" onclick="speakDoctor('{{ doc[1] }}', '{{ doc[4] }}', {{ 'true' if doc[8] else 'false' }})">{{ t.speak }}</button>
            </div>
        </div>
    </div>
    {% endfor %}
    {% endif %}
    
{% elif tab == 'blood' %}
    <div class="section-header blood">🩸 Blood Banks — {{ banks|length }}</div>
    {% for bank in banks %}
    <div class="card blood" data-search="{{ bank[1] }} {{ bank[2] }}">
        <div class="card-header">
            <div style="flex: 1;">
                <div class="card-title">🩸 {{ bank[1] }}</div>
                <div class="card-distance">📍 {{ bank[5] }} {{ t.km_away }}</div>
                <div class="card-info">🏠 {{ bank[2] }}, {{ bank[3] }}</div>
                <div class="card-phone">📞 {{ bank[4] }}</div>
                <div class="card-timing">🕐 {{ bank[7] }} — {{ bank[8] }}</div>
                <div class="card-badge groups">🩸 {{ bank[9] }}</div>
            </div>
            <div class="card-actions">
                <div class="card-badge {% if bank[6] %}open{% else %}closed{% endif %}">
                    {% if bank[6] %}{{ t.open }}{% else %}{{ t.closed }}{% endif %}
                </div><br>
                <a href="tel:{{ bank[4] }}" class="call-btn">{{ t.call }}</a>
            </div>
        </div>
    </div>
    {% endfor %}
    
{% elif tab == 'checkup' %}
    <div class="section-header checkup">🏥 Checkup Centers — {{ centers|length }}</div>
    {% for c in centers %}
    <div class="card checkup" data-search="{{ c[1] }} {{ c[2] }}">
        <div class="card-header">
            <div style="flex: 1;">
                <div class="card-title">🏥 {{ c[1] }}</div>
                <div class="card-distance">📍 {{ c[5] }} {{ t.km_away }}</div>
                <div class="card-info">🏠 {{ c[2] }}, {{ c[3] }}</div>
                <div class="card-phone">📞 {{ c[4] }}</div>
                <div class="card-timing">🕐 {{ c[7] }} — {{ c[8] }}</div>
                <div class="card-badge medicines">✅ {{ c[9] }}</div>
                <div class="card-badge groups">💰 {{ c[10] }}</div>
            </div>
            <div class="card-actions">
                <div class="card-badge {% if c[6] %}open{% else %}closed{% endif %}">
                    {% if c[6] %}{{ t.open }}{% else %}{{ t.closed }}{% endif %}
                </div><br>
                <a href="tel:{{ c[4] }}" class="call-btn">{{ t.call }}</a>
            </div>
        </div>
    </div>
    {% endfor %}
    
{% elif tab == 'medical' %}
    <div class="section-header medical">💊 Medical Stores — {{ stores|length }}</div>
    {% for s in stores %}
    <div class="card medical" data-search="{{ s[1] }} {{ s[2] }}">
        <div class="card-header">
            <div style="flex: 1;">
                <div class="card-title">💊 {{ s[1] }}</div>
                <div class="card-distance">📍 {{ s[5] }} {{ t.km_away }}</div>
                <div class="card-info">🏠 {{ s[2] }}, {{ s[3] }}</div>
                <div class="card-phone">📞 {{ s[4] }}</div>
                <div class="card-timing">🕐 {{ s[7] }} — {{ s[8] }}</div>
                <div class="card-badge medicines">✅ {{ s[9] }}</div>
            </div>
            <div class="card-actions">
                <div class="card-badge {% if s[6] %}open{% else %}closed{% endif %}">
                    {% if s[6] %}{{ t.open }}{% else %}{{ t.closed }}{% endif %}
                </div><br>
                <a href="tel:{{ s[4] }}" class="call-btn">{{ t.call }}</a>
            </div>
        </div>
    </div>
    {% endfor %}
{% endif %}

<div id="noResults" class="no-results" style="display: none;">{{ t.no_results }}</div>

<script>
    const currentLang = "{{ lang }}";
    function changeLanguage(lang) {
        const url = new URL(window.location.href);
        url.searchParams.set('lang', lang);
        window.location.href = url.toString();
    }
    function filterCards() {
        const query = document.getElementById("searchBox").value.toLowerCase();
        const cards = document.querySelectorAll(".card");
        let visible = 0;
        cards.forEach(c => {
            const text = c.dataset.search.toLowerCase();
            if (text.includes(query)) { c.style.display = "block"; visible++; }
            else { c.style.display = "none"; }
        });
        document.getElementById("noResults").style.display = visible === 0 ? "block" : "none";
    }
    function speakText(text) {
        const audio = new Audio(`/voice?text=${encodeURIComponent(text)}&lang=${currentLang}`);
        audio.play().catch(e => {
            if ('speechSynthesis' in window) {
                const u = new SpeechSynthesisUtterance(text);
                u.lang = currentLang === "hi" ? "hi-IN" : currentLang;
                speechSynthesis.speak(u);
            }
        });
    }
    function speakDoctor(name, hospital, isPresent) {
        let msg;
        if (currentLang === "hi") {
            msg = isPresent ? `${name} ${hospital} में मौजूद हैं।` : `${name} ${hospital} में अभी नहीं हैं।`;
        } else {
            msg = isPresent ? `${name} is present at ${hospital}.` : `${name} is not available at ${hospital}.`;
        }
        speakText(msg);
    }
    function speakCurrentTab() {
        const cards = Array.from(document.querySelectorAll(".card")).filter(c => c.style.display !== 'none');
        if (cards.length === 0) { speakText("कुछ नहीं मिला"); return; }
        let msg = currentLang === "hi" ? `${cards.length} विकल्प हैं। ` : `${cards.length} options. `;
        cards.slice(0, 10).forEach((c, i) => {
            const title = c.querySelector(".card-title").textContent.trim();
            msg += `${i + 1}. ${title}. `;
        });
        speakText(msg);
    }
</script>

</body>
</html>
"""
# ============================================
# DOCTOR PAGE (QR scan ke liye - GPS check)
# ============================================

DOCTOR_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ doctor[1] }} - Doctor Live</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f4f8; padding: 20px; }
        .container { max-width: 500px; margin: 0 auto; }
        .header { background: #1e3a8a; color: white; padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
        .header h1 { font-size: 24px; }
        .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        .doctor-name { font-size: 22px; color: #1e293b; font-weight: bold; margin-bottom: 10px; }
        .doctor-info { color: #64748b; font-size: 14px; margin-bottom: 5px; }
        .medicines { background: #f3e8ff; color: #7c3aed; padding: 10px; border-radius: 8px; font-size: 13px; margin-top: 15px; }
        .status-box { text-align: center; padding: 25px; border-radius: 10px; margin: 20px 0; }
        .status-box.present { background: #dcfce7; }
        .status-box.absent { background: #fee2e2; }
        .status-text { font-size: 24px; font-weight: bold; }
        .status-text.present { color: #166534; }
        .status-text.absent { color: #991b1b; }
        .btn { display: block; width: 100%; padding: 16px; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 15px; text-align: center; margin-top: 12px; border: none; cursor: pointer; }
        .btn.green { background: #22c55e; color: white; }
        .btn.red { background: #ef4444; color: white; }
        .btn.back { background: #e2e8f0; color: #1e293b; font-size: 13px; padding: 12px; }
        .secure-badge { background: #dcfce7; color: #166534; padding: 8px; border-radius: 8px; font-size: 12px; text-align: center; margin-bottom: 15px; }
        .gps-info { background: #fef3c7; color: #92400e; padding: 12px; border-radius: 8px; font-size: 13px; margin-top: 15px; text-align: center; font-weight: bold; }
        .gps-success { background: #dcfce7; color: #166534; }
        .gps-error { background: #fee2e2; color: #991b1b; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Doctor Live</h1>
            <p style="font-size: 13px; color: #cbd5e1; margin-top: 5px;">Doctor Status Panel</p>
        </div>
        
        <div class="card">
            <div class="secure-badge">🔐 Verified Doctor — GPS Check Required</div>
            
            <div class="doctor-name">👨‍⚕️ {{ doctor[1] }}</div>
            <div class="doctor-info">🎓 {{ doctor[3] }} — {{ doctor[2] }}</div>
            <div class="doctor-info">🏥 {{ doctor[4] }} ({{ doctor[5] }})</div>
            <div class="doctor-info">📍 {{ doctor[6] }}</div>
            
            {% if doctor[7] %}
            <div class="medicines">💊 {{ doctor[7] }}</div>
            {% endif %}
            
            <div class="status-box {% if doctor[8] %}present{% else %}absent{% endif %}">
                <div class="status-text {% if doctor[8] %}present{% else %}absent{% endif %}">
                    {% if doctor[8] %}🟢 PRESENT{% else %}🔴 ABSENT{% endif %}
                </div>
            </div>
            
            <div id="gpsStatus" class="gps-info">📍 GPS location check ho raha hai...</div>
            
            <div id="actionButtons" style="display: none;">
                {% if not doctor[8] %}
                <button class="btn green" onclick="markPresent()">✅ Mark Present</button>
                {% else %}
                <button class="btn red" onclick="markAbsent()">🔴 Mark Absent</button>
                {% endif %}
            </div>
            
            <a href="/" class="btn back">← Back to Home</a>
        </div>
    </div>
    
    <script>
        const HOSPITAL_LAT = {{ doctor[10] or 0 }};
        const HOSPITAL_LNG = {{ doctor[11] or 0 }};
        const TOKEN = "{{ doctor[9] }}";
        const DOCTOR_ID = {{ doctor[0] }};
        const ALLOWED = 50000000;  // Testing ke liye 50,000 km
        
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(onGPSSuccess, onGPSError,
                { enableHighAccuracy: true, timeout: 10000 });
        } else {
            document.getElementById("gpsStatus").className = "gps-info gps-error";
            document.getElementById("gpsStatus").innerHTML = "❌ Aapka browser GPS support nahi karta";
        }
        
        function onGPSSuccess(position) {
            const userLat = position.coords.latitude;
            const userLng = position.coords.longitude;
            const distance = calculateDistance(userLat, userLng, HOSPITAL_LAT, HOSPITAL_LNG);
            const statusEl = document.getElementById("gpsStatus");
            
            if (distance <= ALLOWED) {
                statusEl.className = "gps-info gps-success";
                statusEl.innerHTML = `✅ Aap hospital ke paas hain (${Math.round(distance)}m)<br>Ab status change kar sakte hain`;
                document.getElementById("actionButtons").style.display = "block";
            } else {
                statusEl.className = "gps-info gps-error";
                statusEl.innerHTML = `❌ Aap hospital se ${Math.round(distance)}m door hain<br>Sirf 100m ke andar hi status change ho sakta hai`;
            }
        }
        
        function onGPSError(error) {
            const statusEl = document.getElementById("gpsStatus");
            statusEl.className = "gps-info gps-error";
            statusEl.innerHTML = "❌ GPS location nahi mili<br>Kripya location permission dein";
        }
        
        function calculateDistance(lat1, lon1, lat2, lon2) {
            const R = 6371000;
            const dLat = (lat2 - lat1) * Math.PI / 180;
            const dLon = (lon2 - lon1) * Math.PI / 180;
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                      Math.sin(dLon/2) * Math.sin(dLon/2);
            return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        }
        
        function markPresent() {
            window.location.href = `/mark-present/${DOCTOR_ID}?token=${TOKEN}`;
        }
        
        function markAbsent() {
            window.location.href = `/mark-absent/${DOCTOR_ID}?token=${TOKEN}`;
        }
    </script>
</body>
</html>
"""


# ============================================
# ACCESS DENIED PAGE
# ============================================

ACCESS_DENIED_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Access Denied</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f4f8; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .card { background: white; padding: 40px; border-radius: 15px; text-align: center; max-width: 450px; }
        .icon { font-size: 70px; margin-bottom: 20px; }
        .title { font-size: 24px; color: #dc2626; font-weight: bold; margin-bottom: 15px; }
        .message { font-size: 15px; color: #475569; line-height: 1.6; }
        a { color: #3b82f6; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">🔒</div>
        <div class="title">Access Denied</div>
        <div class="message">
            Ye page sirf <strong>doctor ke QR code se</strong> khul sakta hai.<br><br>
            <a href="/">← Wapas home page pe jaayein</a>
        </div>
    </div>
</body>
</html>
"""


# ============================================
# ROUTES
# ============================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template_string(LOGIN_PAGE,
            app_name=t("app_name", "hi"), tagline=t("tagline", "hi"),
            mobile_label=t("mobile_label", "hi"), send_otp=t("send_otp", "hi"),
            otp_label=t("otp_label", "hi"), verify=t("verify", "hi"),
            step="mobile")
    
    mobile = request.form.get("mobile", "").strip()
    otp = request.form.get("otp", "").strip()
    
    if otp:
        if verify_otp(mobile, otp):
            user = get_or_create_user(mobile)
            session["user_id"] = user[0]
            session["mobile"] = mobile
            session["language"] = user[1]
            return redirect(url_for("select_language_page"))
        else:
            demo_otp = generate_otp()
            save_otp(mobile, demo_otp)
            return render_template_string(LOGIN_PAGE,
                app_name=t("app_name", "hi"), tagline=t("tagline", "hi"),
                otp_label=t("otp_label", "hi"), verify=t("verify", "hi"),
                step="otp", mobile=mobile, demo_otp=demo_otp,
                error="❌ Galat OTP! Dobara try karein.")
    
    if not mobile or len(mobile) != 10 or not mobile.isdigit():
        return render_template_string(LOGIN_PAGE,
            app_name=t("app_name", "hi"), tagline=t("tagline", "hi"),
            mobile_label=t("mobile_label", "hi"), send_otp=t("send_otp", "hi"),
            step="mobile", error="❌ Sahi 10-digit mobile number daalein!")
    
    demo_otp = generate_otp()
    save_otp(mobile, demo_otp)
    print(f"\n📱 OTP for {mobile}: {demo_otp}\n")
    
    return render_template_string(LOGIN_PAGE,
        app_name=t("app_name", "hi"), tagline=t("tagline", "hi"),
        otp_label=t("otp_label", "hi"), verify=t("verify", "hi"),
        step="otp", mobile=mobile, demo_otp=demo_otp)


@app.route("/select-language", methods=["GET", "POST"])
def select_language_page():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        lang = request.form.get("language", "hi")
        update_user_language(session["mobile"], lang)
        session["language"] = lang
        return redirect(url_for("home"))
    return render_template_string(LANGUAGE_PAGE)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    lang = request.args.get("lang", session.get("language", "hi"))
    session["language"] = lang
    tab = request.args.get("tab", "doctors")
    
    all_doctors = get_all_doctors()
    govt_doctors = [d for d in all_doctors if d[5] == "Government"]
    pvt_doctors = [d for d in all_doctors if d[5] == "Private"]
    
    banks = get_all_blood_banks()
    centers = get_all_checkup_centers()
    stores = get_all_medical_stores()
    
    t_dict = {
        "app_name": t("app_name", lang), "tagline": t("tagline", lang),
        "doctors": t("doctors", lang), "blood_banks": t("blood_banks", lang),
        "checkup": t("checkup", lang), "medical": t("medical", lang),
        "govt": t("govt", lang), "private": t("private", lang),
        "present": t("present", lang), "absent": t("absent", lang),
        "speak": t("speak", lang), "speak_all": t("speak_all", lang),
        "open": t("open", lang), "closed": t("closed", lang),
        "km_away": t("km_away", lang), "call": t("call", lang),
        "search": t("search", lang), "no_results": t("no_results", lang),
        "logout": t("logout", lang),
    }
    
    return render_template_string(HOME_PAGE, lang=lang, tab=tab, t=t_dict,
        govt_doctors=govt_doctors, pvt_doctors=pvt_doctors,
        banks=banks, centers=centers, stores=stores)


@app.route("/doctor/<int:doctor_id>")
def doctor_page(doctor_id):
    token = request.args.get("token", "")
    if not token:
        return render_template_string(ACCESS_DENIED_PAGE), 403
    doctor = get_doctor(doctor_id)
    if not doctor or doctor[9] != token:
        return render_template_string(ACCESS_DENIED_PAGE), 403
    return render_template_string(DOCTOR_PAGE, doctor=doctor)


@app.route("/mark-present/<int:doctor_id>")
def mark_present(doctor_id):
    token = request.args.get("token", "")
    doctor = get_doctor(doctor_id)
    if not doctor or doctor[9] != token:
        return render_template_string(ACCESS_DENIED_PAGE), 403
    set_doctor_status(doctor_id, 1)
    return redirect(url_for("doctor_page", doctor_id=doctor_id, token=token))


@app.route("/mark-absent/<int:doctor_id>")
def mark_absent_route(doctor_id):
    token = request.args.get("token", "")
    doctor = get_doctor(doctor_id)
    if not doctor or doctor[9] != token:
        return render_template_string(ACCESS_DENIED_PAGE), 403
    set_doctor_status(doctor_id, 0)
    return redirect(url_for("doctor_page", doctor_id=doctor_id, token=token))


@app.route("/voice")
def voice():
    try:
        from gtts import gTTS
        text = request.args.get("text", "")
        lang = request.args.get("lang", "hi")
        if not text:
            return "", 400
        lang_map = {"hi": "hi", "en": "en", "bn": "bn", "ta": "ta",
                    "te": "te", "mr": "mr", "gu": "gu", "kn": "kn",
                    "ml": "ml", "pa": "pa"}
        gtts_lang = lang_map.get(lang, "hi")
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return send_file(fp, mimetype="audio/mpeg")
    except Exception as e:
        print(f"Voice error: {e}")
        return "", 500


# ============================================
# DEBUG ENDPOINTS (Testing ke liye)
# ============================================

@app.route("/debug-tokens")
def debug_tokens():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, token FROM doctors ORDER BY id")
    doctors = cursor.fetchall()
    conn.close()
    
    html = "<html><body style='font-family:Arial;padding:20px'>"
    html += "<h2>🔍 Render Database Tokens</h2>"
    html += f"<p><b>Mode:</b> {'PostgreSQL' if DATABASE_URL else 'SQLite'}</p>"
    html += "<table border='1' cellpadding='10' style='border-collapse:collapse'>"
    html += "<tr><th>ID</th><th>Name</th><th>Token</th></tr>"
    for doc in doctors:
        token_display = doc[2] if doc[2] else "<span style='color:red'>NULL</span>"
        html += f"<tr><td>{doc[0]}</td><td>{doc[1]}</td><td><code>{token_display}</code></td></tr>"
    html += "</table></body></html>"
    return html


@app.route("/fix-tokens")
def fix_tokens():
    conn = get_connection()
    cursor = conn.cursor()
    p = ph()
    cursor.execute(f"SELECT id FROM doctors WHERE token IS NULL OR token = ''")
    missing = cursor.fetchall()
    
    for (doc_id,) in missing:
        token = generate_token()
        cursor.execute(f"UPDATE doctors SET token = {p} WHERE id = {p}", (token, doc_id))
    
    conn.commit()
    cursor.execute("SELECT id, name, token FROM doctors ORDER BY id")
    doctors = cursor.fetchall()
    conn.close()
    
    html = "<h2>✅ Tokens Fixed!</h2><table border='1' cellpadding='10'>"
    html += "<tr><th>ID</th><th>Name</th><th>Token</th></tr>"
    for doc in doctors:
        html += f"<tr><td>{doc[0]}</td><td>{doc[1]}</td><td><code>{doc[2]}</code></td></tr>"
    html += "</table><br><a href='/debug-tokens'>Check again</a>"
    return html


# ============================================
# SERVER START
# ============================================

if __name__ == "__main__":
    base_url = get_base_url()
    print("\n" + "=" * 60)
    print("🏥 DOCTOR LIVE SERVER")
    print("=" * 60)
    print(f"\n📱 URL: {base_url}")
    print(f"💻 Local: http://localhost:5000")
    print(f"\n🛑 Band karne ke liye Ctrl+C dabayein")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False)