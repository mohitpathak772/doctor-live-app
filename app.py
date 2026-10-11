# ============================================
# app.py
# Doctor Live - Main App
# Features: Search + Filter + Voice + QR Scan + Reset All
# ============================================

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from voice import speak, speak_doctor_status, speak_all_present_doctors
from qr_system import scan_qr, mark_absent

DB_NAME = "doctors.db"


# ============================================
# Database Functions
# ============================================

def get_all_doctors():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, specialization, degree, hospital_name, 
               hospital_type, city, medicines, is_present
        FROM doctors
        ORDER BY hospital_type, name
    """)
    doctors = cursor.fetchall()
    conn.close()
    return doctors


def update_doctor_status(doctor_id, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE doctors SET is_present = ? WHERE id = ?", 
                   (status, doctor_id))
    conn.commit()
    conn.close()


# ============================================
# Main App Window
# ============================================

class DoctorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏥 Doctor Live - Patient View")
        self.root.geometry("1050x700")
        self.root.configure(bg="#f0f4f8")
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.refresh_doctors())
        
        self.create_header()
        self.create_search_box()
        self.create_filter_buttons()
        self.create_doctor_list()
        self.refresh_doctors()
    
    # ----------------------------------------
    # Header
    # ----------------------------------------
    def create_header(self):
        header = tk.Frame(self.root, bg="#1e3a8a", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        title = tk.Label(
            header, text="🏥 Doctor Live",
            font=("Arial", 24, "bold"),
            bg="#1e3a8a", fg="white"
        )
        title.pack(side="left", padx=20, pady=15)
        
        subtitle = tk.Label(
            header,
            text="Doctor hai ya nahi — pehle check karein, phir niklein!",
            font=("Arial", 12),
            bg="#1e3a8a", fg="#cbd5e1"
        )
        subtitle.pack(side="left", padx=10)
        
        legend = tk.Frame(header, bg="#1e3a8a")
        legend.pack(side="right", padx=20)
        
        tk.Label(legend, text="🟢 Present", font=("Arial", 11, "bold"),
                 bg="#1e3a8a", fg="#22c55e").pack(side="left", padx=5)
        tk.Label(legend, text="🔴 Absent", font=("Arial", 11, "bold"),
                 bg="#1e3a8a", fg="#ef4444").pack(side="left", padx=5)
    
    # ----------------------------------------
    # Search Box
    # ----------------------------------------
    def create_search_box(self):
        search_frame = tk.Frame(self.root, bg="#f0f4f8")
        search_frame.pack(fill="x", padx=20, pady=(15, 5))
        
        tk.Label(
            search_frame, text="🔍 Search:",
            font=("Arial", 12, "bold"),
            bg="#f0f4f8", fg="#1e293b"
        ).pack(side="left", padx=5)
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 12),
            width=35
        )
        search_entry.pack(side="left", padx=5, ipady=6)
        
        tk.Label(
            search_frame,
            text="(Doctor ka naam, specialization, ya hospital type karein)",
            font=("Arial", 10, "italic"),
            bg="#f0f4f8", fg="#64748b"
        ).pack(side="left", padx=8)
    
    # ----------------------------------------
    # Filter + Buttons
    # ----------------------------------------
    def create_filter_buttons(self):
        filter_frame = tk.Frame(self.root, bg="#f0f4f8")
        filter_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(filter_frame, text="Filter:", font=("Arial", 12, "bold"),
                 bg="#f0f4f8").pack(side="left", padx=5)
        
        self.filter_var = tk.StringVar(value="All")
        
        for text, value in [("Sab", "All"), ("🏛️ Sarkari", "Government"), 
                            ("🏥 Private", "Private")]:
            rb = tk.Radiobutton(
                filter_frame, text=text,
                variable=self.filter_var, value=value,
                font=("Arial", 11), bg="#f0f4f8",
                command=self.refresh_doctors, cursor="hand2"
            )
            rb.pack(side="left", padx=8)
        
        # Refresh button
        refresh_btn = tk.Button(
            filter_frame, text="🔄 Refresh",
            font=("Arial", 11, "bold"),
            bg="#3b82f6", fg="white", padx=15, pady=5,
            cursor="hand2", command=self.refresh_doctors
        )
        refresh_btn.pack(side="right", padx=5)
        
        # 🔴 Reset All button (NAYA)
        reset_btn = tk.Button(
            filter_frame, text="🔴 Reset All",
            font=("Arial", 11, "bold"),
            bg="#dc2626", fg="white", padx=15, pady=5,
            cursor="hand2", command=self.reset_all_doctors
        )
        reset_btn.pack(side="right", padx=5)
        
        # 🔊 Voice button
        voice_btn = tk.Button(
            filter_frame, text="🔊 Saare Present",
            font=("Arial", 11, "bold"),
            bg="#7c3aed", fg="white", padx=15, pady=5,
            cursor="hand2", command=speak_all_present_doctors
        )
        voice_btn.pack(side="right", padx=5)
        
        # 📷 QR Scan button
        qr_btn = tk.Button(
            filter_frame, text="📷 QR Scan",
            font=("Arial", 11, "bold"),
            bg="#059669", fg="white", padx=15, pady=5,
            cursor="hand2", command=self.open_qr_scanner
        )
        qr_btn.pack(side="right", padx=5)
    
    # ----------------------------------------
    # Doctor List
    # ----------------------------------------
    def create_doctor_list(self):
        main_frame = tk.Frame(self.root, bg="#f0f4f8")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.canvas = tk.Canvas(main_frame, bg="#f0f4f8", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", 
                                  command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f4f8")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind_all("<MouseWheel>", 
                            lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    def refresh_doctors(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        doctors = get_all_doctors()
        filter_val = self.filter_var.get()
        search_text = self.search_var.get().lower().strip()
        
        count = 0
        for doc in doctors:
            doc_id, name, spec, deg, hosp, htype, city, meds, present = doc
            
            if filter_val != "All" and htype != filter_val:
                continue
            
            if search_text:
                combined = f"{name} {spec} {deg} {hosp} {city}".lower()
                if search_text not in combined:
                    continue
            
            self.create_doctor_card(doc_id, name, spec, deg, hosp, htype, city, meds, present)
            count += 1
        
        if count == 0:
            tk.Label(
                self.scrollable_frame,
                text="😕 Koi doctor nahi mila.\nSearch ya filter change karein.",
                font=("Arial", 14), bg="#f0f4f8", fg="#64748b",
                justify="center"
            ).pack(pady=50)
    
    def create_doctor_card(self, doc_id, name, spec, deg, hosp, htype, city, meds, present):
        if present:
            border_color = "#22c55e"
            status_text = "🟢 PRESENT"
            status_color = "#22c55e"
        else:
            border_color = "#ef4444"
            status_text = "🔴 ABSENT"
            status_color = "#ef4444"
        
        card = tk.Frame(
            self.scrollable_frame, bg="white", bd=0,
            highlightbackground=border_color, highlightthickness=2
        )
        card.pack(fill="x", padx=10, pady=8)
        
        left = tk.Frame(card, bg="white")
        left.pack(side="left", fill="both", expand=True, padx=15, pady=12)
        
        tk.Label(left, text=f"👨‍⚕️  {name}", font=("Arial", 15, "bold"),
                 bg="white", fg="#1e293b", anchor="w").pack(anchor="w")
        
        tk.Label(left, text=f"🎓  {deg} — {spec}", font=("Arial", 11),
                 bg="white", fg="#475569", anchor="w").pack(anchor="w", pady=(3, 0))
        
        hospital_icon = "🏛️" if htype == "Government" else "🏥"
        tk.Label(left, text=f"{hospital_icon}  {hosp} ({htype})",
                 font=("Arial", 11), bg="white", fg="#475569", anchor="w").pack(anchor="w", pady=(3, 0))
        
        tk.Label(left, text=f"📍  {city}", font=("Arial", 10),
                 bg="white", fg="#64748b", anchor="w").pack(anchor="w", pady=(3, 0))
        
        tk.Label(left, text=f"💊  {meds}", font=("Arial", 10, "italic"),
                 bg="white", fg="#7c3aed", anchor="w").pack(anchor="w", pady=(5, 0))
        
        right = tk.Frame(card, bg="white")
        right.pack(side="right", padx=15, pady=12)
        
        tk.Label(right, text=status_text, font=("Arial", 13, "bold"),
                 bg="white", fg=status_color).pack()
        
        tk.Button(
            right, text="🔊 Sunno", font=("Arial", 9, "bold"),
            bg="#7c3aed", fg="white", cursor="hand2",
            command=lambda: speak_doctor_status(name)
        ).pack(pady=(8, 0))
        
        tk.Button(
            right, text="🔄 Toggle", font=("Arial", 9),
            bg="#e2e8f0", fg="#1e293b", cursor="hand2",
            command=lambda: self.toggle_status(doc_id, present)
        ).pack(pady=(5, 0))
    
    def toggle_status(self, doc_id, current_status):
        new_status = 0 if current_status else 1
        update_doctor_status(doc_id, new_status)
        self.refresh_doctors()
    
    # ----------------------------------------
    # ⭐ RESET ALL DOCTORS (NAYA)
    # ----------------------------------------
    def reset_all_doctors(self):
        """Saare doctors ko ABSENT kar deta hai"""
        
        answer = messagebox.askyesno(
            "⚠️ Confirm Karein",
            "Kya aap SAARE doctors ko ABSENT mark karna chahte hain?\n\n"
            "Ye raat ko hospital band hone par use hota hai.\n"
            "Subah doctors dobara apna QR scan karke Present ho sakte hain."
        )
        
        if not answer:
            return
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE doctors SET is_present = 0")
        conn.commit()
        conn.close()
        
        self.refresh_doctors()
        
        messagebox.showinfo(
            "✅ Ho Gaya",
            "Saare doctors ab ABSENT mark ho gaye hain.\n\n"
            "Subah doctors QR scan karke Present ho sakte hain."
        )
    
    # ----------------------------------------
    # QR Scanner
    # ----------------------------------------
    def open_qr_scanner(self):
        scan_window = tk.Toplevel(self.root)
        scan_window.title("📷 QR Scan - Doctor Login")
        scan_window.geometry("520x480")
        scan_window.configure(bg="#f0f4f8")
        scan_window.transient(self.root)
        scan_window.grab_set()
        
        tk.Label(
            scan_window, text="📷 QR Scan",
            font=("Arial", 22, "bold"),
            bg="#059669", fg="white",
            pady=15
        ).pack(fill="x")
        
        tk.Label(
            scan_window,
            text="Doctor apna QR code scan karein",
            font=("Arial", 12),
            bg="#f0f4f8", fg="#475569"
        ).pack(pady=(15, 5))
        
        tk.Label(
            scan_window,
            text="QR Data type karein ya Doctor ID daalein:",
            font=("Arial", 11, "bold"),
            bg="#f0f4f8", fg="#1e293b"
        ).pack(pady=(10, 5))
        
        qr_input = tk.Entry(
            scan_window, font=("Arial", 14),
            width=30, justify="center"
        )
        qr_input.pack(pady=5, ipady=8)
        qr_input.focus()
        
        tk.Label(
            scan_window,
            text="💡 Udaharan: 3   ya   DOCTOR-3",
            font=("Arial", 10, "italic"),
            bg="#f0f4f8", fg="#64748b"
        ).pack(pady=(5, 15))
        
        result_label = tk.Label(
            scan_window, text="",
            font=("Arial", 12, "bold"),
            bg="#f0f4f8", fg="#1e293b",
            wraplength=460
        )
        result_label.pack(pady=10)
        
        def do_scan():
            data = qr_input.get().strip()
            
            if not data:
                result_label.config(text="⚠️ Kuch type karein!", fg="#ef4444")
                return
            
            if data.isdigit():
                data = f"DOCTOR-{data}"
            
            success, message = scan_qr(data)
            
            if success:
                result_label.config(text=message, fg="#22c55e")
                qr_input.delete(0, tk.END)
                self.root.after(1500, self.refresh_doctors)
            else:
                result_label.config(text=message, fg="#ef4444")
        
        tk.Button(
            scan_window, text="✅ Mark Present",
            font=("Arial", 13, "bold"),
            bg="#059669", fg="white",
            padx=30, pady=10,
            cursor="hand2", command=do_scan
        ).pack(pady=10)
        
        qr_input.bind("<Return>", lambda e: do_scan())
        
        tk.Button(
            scan_window, text="❌ Band Karein",
            font=("Arial", 10),
            bg="#e2e8f0", fg="#1e293b",
            padx=20, pady=5,
            cursor="hand2", command=scan_window.destroy
        ).pack(pady=5)


# ============================================
# App Chalu Karein
# ============================================

if __name__ == "__main__":
    root = tk.Tk()
    app = DoctorApp(root)
    root.mainloop()