# ============================================
# server.py
# Flask Web Server - Doctor apne phone se status update kare
# SQLite (local) + PostgreSQL (cloud) dono support
# ============================================

from flask import Flask, render_template_string
import socket
import os
from datetime import datetime
from database import get_connection, ph

app = Flask(__name__)


# ============================================
# Helper Functions
# ============================================

def get_doctor(doctor_id):
    """Doctor ki info laata hai"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id, name, specialization, hospital_name, is_present
        FROM doctors WHERE id = {ph()}
    """, (doctor_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def get_all_doctors():
    """Saare doctors laata hai"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, specialization, hospital_name, is_present
        FROM doctors ORDER BY id
    """)
    result = cursor.fetchall()
    conn.close()
    return result


def set_doctor_status(doctor_id, status):
    """Doctor ka status update karta hai"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE doctors SET is_present = {ph()} WHERE id = {ph()}",
        (status, doctor_id)
    )
    conn.commit()
    conn.close()


def get_local_ip():
    """PC ka local IP address nikalta hai"""
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


# ============================================
# HTML Templates
# ============================================

HOME_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Doctor Live - Server</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f4f8; padding: 20px; }
        .header { background: #1e3a8a; color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
        .header h1 { font-size: 28px; }
        .header p { font-size: 14px; color: #cbd5e1; margin-top: 5px; }
        .ip-box { background: #fef3c7; border: 2px solid #f59e0b; padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
        .ip-box .label { font-size: 14px; color: #78350f; }
        .ip-box .ip { font-size: 22px; font-weight: bold; color: #92400e; margin-top: 5px; word-break: break-all; }
        .ip-box .hint { font-size: 12px; color: #78350f; margin-top: 8px; }
        .doctor-list { display: grid; gap: 15px; }
        .doctor-card { background: white; padding: 20px; border-radius: 10px; border-left: 5px solid #ef4444; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
        .doctor-card.present { border-left-color: #22c55e; }
        .doctor-info h3 { color: #1e293b; font-size: 18px; }
        .doctor-info p { color: #64748b; font-size: 13px; margin-top: 3px; }
        .status { font-weight: bold; font-size: 14px; padding: 5px 12px; border-radius: 20px; display: inline-block; }
        .status.present { background: #dcfce7; color: #166534; }
        .status.absent { background: #fee2e2; color: #991b1b; }
        .btn { background: #3b82f6; color: white; padding: 8px 16px; border-radius: 5px; text-decoration: none; font-weight: bold; font-size: 13px; display: inline-block; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 Doctor Live Server</h1>
        <p>Doctor apne phone se status update kar sakta hai</p>
    </div>
    
    <div class="ip-box">
        <div class="label">📱 Doctor apne phone mein ye URL kholein:</div>
        <div class="ip">{{ base_url }}</div>
        <div class="hint">(Phone aur server same network ya internet pe hone chahiye)</div>
    </div>
    
    <h2 style="color: #1e293b; margin-bottom: 15px;">📋 Saare Doctors</h2>
    <div class="doctor-list">
        {% for doc in doctors %}
        <div class="doctor-card {% if doc[4] %}present{% endif %}">
            <div class="doctor-info">
                <h3>👨‍⚕️ {{ doc[1] }}</h3>
                <p>🎓 {{ doc[2] }}</p>
                <p>🏥 {{ doc[3] }}</p>
            </div>
            <div style="text-align: right;">
                <div class="status {% if doc[4] %}present{% else %}absent{% endif %}">
                    {% if doc[4] %}🟢 PRESENT{% else %}🔴 ABSENT{% endif %}
                </div>
                <br>
                <a href="/doctor/{{ doc[0] }}" class="btn">Manage →</a>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

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
        .header p { font-size: 14px; color: #cbd5e1; margin-top: 8px; }
        .card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        .doctor-name { font-size: 22px; color: #1e293b; font-weight: bold; margin-bottom: 10px; }
        .doctor-info { color: #64748b; font-size: 14px; margin-bottom: 5px; }
        .status-box { text-align: center; padding: 25px; border-radius: 10px; margin: 25px 0; }
        .status-box.present { background: #dcfce7; }
        .status-box.absent { background: #fee2e2; }
        .status-text { font-size: 24px; font-weight: bold; }
        .status-text.present { color: #166534; }
        .status-text.absent { color: #991b1b; }
        .status-time { font-size: 12px; color: #64748b; margin-top: 8px; }
        .btn { display: block; width: 100%; padding: 18px; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 16px; text-align: center; margin-top: 12px; }
        .btn.green { background: #22c55e; color: white; }
        .btn.red { background: #ef4444; color: white; }
        .btn.back { background: #e2e8f0; color: #1e293b; font-size: 14px; padding: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Doctor Live</h1>
            <p>Status Update Panel</p>
        </div>
        
        <div class="card">
            <div class="doctor-name">👨‍⚕️ {{ doctor[1] }}</div>
            <div class="doctor-info">🎓 {{ doctor[2] }}</div>
            <div class="doctor-info">🏥 {{ doctor[3] }}</div>
            
            <div class="status-box {% if doctor[4] %}present{% else %}absent{% endif %}">
                <div class="status-text {% if doctor[4] %}present{% else %}absent{% endif %}">
                    {% if doctor[4] %}🟢 PRESENT{% else %}🔴 ABSENT{% endif %}
                </div>
                <div class="status-time">Last updated: {{ time }}</div>
            </div>
            
            {% if not doctor[4] %}
            <a href="/mark-present/{{ doctor[0] }}" class="btn green">✅ Mark Present (Aaya hoon)</a>
            {% else %}
            <a href="/mark-absent/{{ doctor[0] }}" class="btn red">🔴 Mark Absent (Ja raha hoon)</a>
            {% endif %}
            
            <a href="/" class="btn back">← Back to List</a>
        </div>
    </div>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="2;url=/doctor/{{ doctor_id }}">
    <title>Success</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f4f8; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .card { background: white; padding: 40px; border-radius: 15px; text-align: center; max-width: 400px; }
        .icon { font-size: 60px; margin-bottom: 20px; }
        .message { font-size: 18px; color: #1e293b; font-weight: bold; }
        .sub { font-size: 14px; color: #64748b; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">✅</div>
        <div class="message">{{ message }}</div>
        <div class="sub">Redirect ho raha hai...</div>
    </div>
</body>
</html>
"""


# ============================================
# Routes
# ============================================

@app.route("/")
def home():
    doctors = get_all_doctors()
    base_url = get_base_url()
    return render_template_string(HOME_PAGE, doctors=doctors, base_url=base_url)


@app.route("/doctor/<int:doctor_id>")
def doctor_page(doctor_id):
    doctor = get_doctor(doctor_id)
    if not doctor:
        return f"<h1>❌ Doctor ID {doctor_id} nahi mila!</h1><a href='/'>← Back</a>", 404
    
    time_now = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    return render_template_string(DOCTOR_PAGE, doctor=doctor, time=time_now)


@app.route("/mark-present/<int:doctor_id>")
def mark_present(doctor_id):
    doctor = get_doctor(doctor_id)
    if not doctor:
        return "<h1>❌ Doctor nahi mila!</h1>", 404
    
    set_doctor_status(doctor_id, 1)
    message = f"{doctor[1]} ab PRESENT hain!"
    return render_template_string(SUCCESS_PAGE, message=message, doctor_id=doctor_id)


@app.route("/mark-absent/<int:doctor_id>")
def mark_absent_route(doctor_id):
    doctor = get_doctor(doctor_id)
    if not doctor:
        return "<h1>❌ Doctor nahi mila!</h1>", 404
    
    set_doctor_status(doctor_id, 0)
    message = f"{doctor[1]} ab ABSENT hain!"
    return render_template_string(SUCCESS_PAGE, message=message, doctor_id=doctor_id)


# ============================================
# Server Chalu Karein
# ============================================

if __name__ == "__main__":
    base_url = get_base_url()
    
    print("\n" + "=" * 60)
    print("🏥 DOCTOR LIVE SERVER CHALU HO RAHA HAI...")
    print("=" * 60)
    print(f"\n📱 URL: {base_url}")
    print(f"💻 Local: http://localhost:5000")
    print(f"\n🛑 Band karne ke liye Ctrl+C dabayein")
    print("=" * 60 + "\n")
    
    app.run(host="0.0.0.0", port=5000, debug=False)