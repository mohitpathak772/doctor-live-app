# ============================================
# voice.py
# App ko bolna sikhata hai - gTTS se (Perfect Hindi)
# ============================================

import sqlite3
import threading
import os
import tempfile
import time

# gTTS import
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("⚠️  gTTS install nahi hai.")

# playsound import (silent audio ke liye)
try:
    from playsound import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    PLAYSOUND_AVAILABLE = False
    print("⚠️  playsound install nahi hai.")

DB_NAME = "doctors.db"


# ============================================
# Audio Play karne ka function
# ============================================

def play_audio_file(file_path):
    """Audio play karta hai - silently (bina Media Player window)"""
    try:
        if PLAYSOUND_AVAILABLE:
            playsound(file_path)
        else:
            # Fallback: Windows Media Player
            os.system(f'start /min "" "{file_path}"')
    except Exception as e:
        print(f"❌ Audio play error: {e}")


# ============================================
# App Bolna (Text to Speech)
# ============================================

def speak(text, lang="hi"):
    """
    App ko bolne ke liye (Hindi mein)
    text: jo bolna hai
    lang: 'hi' = Hindi, 'en' = English
    """
    
    def _speak():
        if not GTTS_AVAILABLE:
            print(f"🔊 [BOLNA]: {text}")
            return
        
        try:
            print(f"🔊 [BOL Raha hai]: {text}")
            
            # gTTS se audio banao
            tts = gTTS(text=text, lang=lang, slow=False)
            
            # Temporary file mein save karo
            temp_file = os.path.join(
                tempfile.gettempdir(), 
                "doctor_live_voice.mp3"
            )
            tts.save(temp_file)
            
            # Play karo
            play_audio_file(temp_file)
            
        except Exception as e:
            print(f"❌ Voice error: {e}")
            print(f"🔊 [BOLNA tha]: {text}")
    
    # Alag thread mein chalao taaki app freeze na ho
    thread = threading.Thread(target=_speak, daemon=True)
    thread.start()


# ============================================
# Doctor Info Bolna
# ============================================

def speak_doctor_status(doctor_name):
    """Kisi specific doctor ka status bolta hai"""
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, specialization, hospital_name, is_present
        FROM doctors
        WHERE name LIKE ?
    """, (f"%{doctor_name}%",))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        speak(f"Maaf kijiye, {doctor_name} naam ka koi doctor nahi mila.")
        return
    
    name, spec, hospital, is_present = result
    
    if is_present:
        message = f"Haan, {name} abhi {hospital} mein hain. Aap aa sakte hain."
    else:
        message = f"Maaf kijiye, {name} abhi {hospital} mein nahi hain. Thodi der baad check karein."
    
    speak(message)


def speak_all_present_doctors():
    """Saare present doctors ki list bolta hai"""
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, hospital_name
        FROM doctors
        WHERE is_present = 1
    """)
    
    doctors = cursor.fetchall()
    conn.close()
    
    if not doctors:
        speak("Abhi koi bhi doctor hospital mein present nahi hai.")
        return
    
    message = f"Abhi {len(doctors)} doctor present hain. "
    for i, (name, hospital) in enumerate(doctors, 1):
        message += f"{i}. {name}, {hospital}. "
    
    speak(message)


def speak_help():
    """Help message bolta hai"""
    message = (
        "Namaste! Main Doctor Live app hoon. "
        "Aap mujhse poochh sakte hain ki kaunsa doctor hospital mein hai ya nahi. "
        "Jaise: Doctor Sharma hai? "
        "Ya phir: Kaun kaun present hai? "
        "Main aapko bata dungi."
    )
    speak(message)


def speak_welcome():
    """App start hone pe welcome message"""
    speak("Namaste! Doctor Live app mein aapka swagat hai.")


# ============================================
# Testing (sirf jab ye file direct chalayein)
# ============================================

if __name__ == "__main__":
    print("🔊 Voice test shuru (gTTS version)...")
    print("⚠️  Internet connection zaroori hai!\n")
    
    print("1. Welcome message")
    speak_welcome()
    time.sleep(6)
    
    print("\n2. Ek doctor ka status")
    speak_doctor_status("Sharma")
    time.sleep(6)
    
    print("\n3. Saare present doctors")
    speak_all_present_doctors()
    time.sleep(6)
    
    print("\n✅ Test complete!")