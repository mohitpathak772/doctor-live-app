# ============================================
# templates.py
# Saare HTML templates - alag file mein
# ============================================

# ============================================
# LOGIN PAGE (Mobile Number)
# ============================================

LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Doctor Live - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card {
            background: white;
            padding: 40px 30px;
            border-radius: 20px;
            max-width: 420px;
            width: 100%;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            text-align: center;
        }
        .logo { font-size: 60px; margin-bottom: 10px; }
        .title {
            font-size: 28px;
            color: #1e3a8a;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .subtitle {
            color: #64748b;
            font-size: 14px;
            margin-bottom: 30px;
        }
        .input-group { margin-bottom: 20px; text-align: left; }
        .input-group label {
            display: block;
            font-size: 14px;
            color: #1e293b;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .input-group input {
            width: 100%;
            padding: 14px 18px;
            border: 2px solid #cbd5e1;
            border-radius: 10px;
            font-size: 16px;
            outline: none;
            transition: border 0.2s;
        }
        .input-group input:focus { border-color: #3b82f6; }
        
        .btn {
            width: 100%;
            padding: 16px;
            background: #1e3a8a;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn:hover { background: #1e40af; }
        .btn:disabled { background: #94a3b8; cursor: not-allowed; }
        
        .info-box {
            background: #fef3c7;
            border: 2px solid #f59e0b;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            font-size: 13px;
            color: #78350f;
            text-align: left;
        }
        .info-box strong { color: #92400e; }
        
        .footer {
            margin-top: 25px;
            font-size: 12px;
            color: #94a3b8;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">🏥</div>
        <div class="title">Doctor Live</div>
        <div class="subtitle">डॉक्टर की उपलब्धता — बिना अस्पताल जाए</div>
        
        <form method="POST" action="/send-otp">
            <div class="input-group">
                <label>📱 Mobile Number</label>
                <input type="tel" name="mobile" placeholder="+91 XXXXX XXXXX" 
                       pattern="[0-9]{10}" maxlength="10" required autofocus>
            </div>
            <button type="submit" class="btn">OTP Bhejein →</button>
        </form>
        
        <div class="info-box">
            💡 <strong>Note:</strong> Ye ek demo app hai. Real OTP nahi bheja jayega — 
            screen pe dikhaya jayega.
        </div>
        
        <div class="footer">Made with ❤️ for India</div>
    </div>
</body>
</html>
"""


# ============================================
# OTP VERIFY PAGE
# ============================================

OTP_PAGE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OTP Verify - Doctor Live</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card {
            background: white;
            padding: 40px 30px;
            border-radius: 20px;
            max-width: 420px;
            width: 100%;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            text-align: center;
        }
        .logo { font-size: 60px; margin-bottom: 10px; }
        .title {
            font-size: 24px;
            color: #1e3a8a;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .subtitle {
            color: #64748b;
            font-size: 14px;
            margin-bottom: 25px;
        }
        .mobile-display {
            background: #dbeafe;
            color: #1e40af;
            padding: 12px;
            border-radius: 10px;
            font-weight: bold;
            margin-bottom: 25px;
            font-size: 15px;
        }
        
        .otp-display {
            background: #fef3c7;
            border: 2px dashed #f59e0b;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 25px;
        }
        .otp-label {
            font-size: 13px;
            color: #78350f;
            margin-bottom: 8px;
        }
        .otp-code {
            font-size: 32px;
            font-weight: bold;
            color: #dc2626;
            letter-spacing: 8px;
            font-family: monospace;
        }
        
        .input-group { margin-bottom: 20px; text-align: left; }
        .input-group label {
            display: block;
            font-size: 14px;
            color: #1e293b;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .input-group input {
            width: 100%;
            padding: 16px;
            border: 2px solid #cbd5e1;
            border-radius: 10px;
            font-size: 22px;
            outline: none;
            text-align: center;
            letter-spacing: 8px;
            font-family: monospace;
        }
        .input-group input:focus { border-color: #3b82f6; }
        
        .btn {
            width: 100%;
            padding: 16px;
            background: #22c55e;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        .btn:hover { background: #16a34a; }
        
        .error {
            background: #fee2e2;
            color: #991b1b;
            padding: 12px;
            border-radius: 8px;
            font-size: 13px;
            margin-bottom: 15px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">📱</div>
        <div class="title">OTP Verify Karein</div>
        <div class="subtitle">Aapke number pe OTP bheja gaya hai</div>
        
        <div class="mobile-display">
            📱 +91 {{ mobile }}
        </div>
        
        <div class="otp-display">
            <div class="otp-label">💡 Demo OTP (asli app mein SMS se aayega):</div>
            <div class="otp-code">{{ otp }}</div>
        </div>
        
        {% if error %}
        <div class="error">❌ {{ error }}</div>
        {% endif %}
        
        <form method="POST" action="/verify-otp">
            <input type="hidden" name="mobile" value="{{ mobile }}">
            <input type="hidden" name="correct_otp" value="{{ otp }}">
            
            <div class="input-group">
                <label>🔐 OTP Daalein</label>
                <input type="text" name="otp" placeholder="______" 
                       maxlength="6" pattern="[0-9]{6}" required autofocus>
            </div>
            
            <button type="submit" class="btn">✅ Verify Karein</button>
        </form>
    </div>
</body>
</html>
"""


# ============================================
# LANGUAGE SELECT PAGE
# ============================================

LANGUAGE_PAGE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Language Select - Doctor Live</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card {
            background: white;
            padding: 35px 25px;
            border-radius: 20px;
            max-width: 450px;
            width: 100%;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        }
        .logo { font-size: 50px; text-align: center; margin-bottom: 10px; }
        .title {
            font-size: 22px;
            color: #1e3a8a;
            font-weight: bold;
            text-align: center;
            margin-bottom: 8px;
        }
        .subtitle {
            color: #64748b;
            font-size: 13px;
            text-align: center;
            margin-bottom: 25px;
        }
        
        .lang-list { display: grid; gap: 10px; margin-bottom: 25px; }
        .lang-option {
            display: block;
            padding: 14px 18px;
            border: 2px solid #cbd5e1;
            border-radius: 10px;
            cursor: pointer;
            font-size: 15px;
            background: white;
            transition: all 0.2s;
            text-align: left;
        }
        .lang-option:hover { border-color: #3b82f6; background: #eff6ff; }
        .lang-option input {
            margin-right: 10px;
            transform: scale(1.3);
            cursor: pointer;
        }
        .lang-option input:checked + span {
            font-weight: bold;
            color: #1e3a8a;
        }
        
        .btn {
            width: 100%;
            padding: 16px;
            background: #1e3a8a;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        .btn:hover { background: #1e40af; }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">🌐</div>
        <div class="title">अपनी भाषा चुनें</div>
        <div class="subtitle">Choose Your Language</div>
        
        <form method="POST" action="/set-language">
            <input type="hidden" name="mobile" value="{{ mobile }}">
            
            <div class="lang-list">
                <label class="lang-option">
                    <input type="radio" name="language" value="hi" checked>
                    <span>🇮🇳 हिंदी (Hindi)</span>
                </label>
                <label class="lang-option">
                    <input type="radio" name="language" value="en">
                    <span>🇬🇧 English</span>
                </label>
                <label class="lang-option">
                    <input type="radio" name="language" value="bn">
                    <span>🇮🇳 বাংলা (Bengali)</span>
                </label>
                <label class="lang-option">
                    <input type="radio" name="language" value="ta">
                    <span>🇮🇳 தமிழ் (Tamil)</span>
                </label>
                <label class="lang-option">
                    <input type="radio" name="language" value="te">
                    <span>🇮🇳 తెలుగు (Telugu)</span>
                </label>
                <label class="lang-option">
                    <input type="radio" name="language" value="mr">
                    <span>🇮🇳 मराठी (Marathi)</span>
                </label>
                <label class="lang-option">
                    <input type="radio" name="language" value="gu">
                    <span>🇮🇳 ગુજરાતી (Gujarati)</span>
                </label>
                <label class="lang-option">
                    <input type="radio" name="language" value="kn">
                    <span>🇮🇳 ಕನ್ನಡ (Kannada)</span>
                </label>
                <label class="lang-option">
                    <input type="radio" name="language" value="ml">
                    <span>🇮🇳 മലയാളം (Malayalam)</span>
                </label>
                <label class="lang-option">
                    <input type="radio" name="language" value="pa">
                    <span>🇮🇳 ਪੰਜਾਬੀ (Punjabi)</span>
                </label>
            </div>
            
            <button type="submit" class="btn">Aage Badhein →</button>
        </form>
    </div>
</body>
</html>
"""