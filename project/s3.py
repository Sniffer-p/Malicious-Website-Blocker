
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import requests
import smtplib
import ssl
import random
import os
import json
import webbrowser
import time
from tkinter.simpledialog import askstring
from PIL import Image, ImageTk


# === CONFIG ===
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts" if os.name == 'nt' else "/etc/hosts"
REDIRECT_IP = "127.0.0.1"
VT_API_KEY = "a083c3132a78e8dc1c17833312ddee6ab0ce203bebc323ac2f08b8b9db20c3b3"
CONFIG_FILE = "config.json"


# === GLOBALS ===
sender_email = "maliciousblocker@gmail.com"
app_password = "nhjshyybikllqrvx"
receiver_email = None
pending_urls = []
current_theme = "darkly"


# === PERSISTENCE HELPERS ===
def save_email(email):
    """Saves the user's email to a config file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump({"receiver_email": email}, f)


def load_email():
    """Loads the user's email from the config file if it exists."""
    global receiver_email
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                receiver_email = config.get("receiver_email")
        except (json.JSONDecodeError, IOError):
            receiver_email = None


# === SPLASH SCREEN ===
def show_splash():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.geometry("520x400+600+300")
    try:
        img = Image.open("animated_background_frame.png").resize((520, 400))
        splash_img = ImageTk.PhotoImage(img)
        lbl = tk.Label(splash, image=splash_img)
        lbl.image = splash_img
        lbl.pack()
    except:
        lbl = tk.Label(splash, text="Malicious Website Blocker", font=("Arial", 20), bg="black", fg="white")
        lbl.pack(fill="both", expand=True)

    splash.after(2500, splash.destroy)
    splash.mainloop()


show_splash()
load_email() # Load email at startup


# === GUI INIT ===
app = tb.Window(themename=current_theme)
app.title("💻 Malicious Website Blocker Tool")
app.geometry("520x600")
app.resizable(False, False)


# === Background Image ===
try:
    bg = Image.open("bg.png").resize((520, 600))
    bg_img = ImageTk.PhotoImage(bg)
    tk.Label(app, image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)
except:
    app.configure(bg="#1f1f1f")


# === HELPERS ===
def get_public_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "Unavailable"


def clean_domain(url):
    return url.replace("http://", "").replace("https://", "").split("/")[0].strip()


def is_malicious(domain):
    try:
        headers = {"x-apikey": VT_API_KEY}
        url = f"https://www.virustotal.com/api/v3/domains/{domain}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            stats = response.json()["data"]["attributes"]["last_analysis_stats"]
            return stats["malicious"] > 0 or stats["suspicious"] > 0
        elif response.status_code == 429:
            messagebox.showwarning("Rate Limit", "VirusTotal rate limit reached. Try again later.")
            time.sleep(15)
    except Exception as e:
        print("VirusTotal Error:", e)
    return False


# === OTP ===
def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(otp):
    global receiver_email
    if not receiver_email:
        email_input = askstring("Your Email", "Enter your email to receive OTP:", parent=app)
        if email_input:
            receiver_email = email_input
            save_email(receiver_email) # Save for future use
        else:
            messagebox.showwarning("Email Required", "An email address is required to proceed.")
            return False
            
    try:
        subject = "🔐 OTP for Blocking Request"
        body = f"Your OTP is: {otp}\n\nValid for 3 minutes."
        message = f"Subject: {subject}\n\n{body}"
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.encode("utf-8"))
        return True
    except Exception as e:
        messagebox.showerror("Email Error", str(e))
        return False


def verify_otp(otp_expected):
    def check():
        if otp_entry.get().strip() == otp_expected:
            otp_window.destroy()
            proceed_to_block()
        else:
            messagebox.showerror("Invalid OTP", "Incorrect OTP entered.")

    otp_window = Toplevel(app)
    otp_window.title("OTP Verification")
    otp_window.geometry("300x150")
    otp_window.configure(bg="#1f1f1f")
    tk.Label(otp_window, text="Enter OTP sent to your email", bg="#1f1f1f", fg="white").pack(pady=10)
    otp_entry = tk.Entry(otp_window, font=("Consolas", 14), justify="center")
    otp_entry.pack()
    tb.Button(otp_window, text="Verify", command=check, bootstyle="success").pack(pady=10)


def start_blocking_with_otp(urls):
    global pending_urls
    pending_urls = urls
    otp = generate_otp()
    if send_otp_email(otp):
        verify_otp(otp)


# === BLOCKING ===
def proceed_to_block():
    try:
        with open(HOSTS_PATH, "r") as f:
            current_hosts = f.read()
        blocked = 0
        with open(HOSTS_PATH, "a") as f:
            for url in pending_urls:
                domain = clean_domain(url)
                if not domain or domain in current_hosts:
                    continue
                if not is_malicious(domain):
                    if not messagebox.askyesno("Confirm", f"'{domain}' does not appear malicious.\nBlock anyway?"):
                        continue
                f.write(f"\n{REDIRECT_IP} {domain}")
                blocked += 1
        messagebox.showinfo("Success", f"{blocked} website(s) blocked.")
    except PermissionError:
        messagebox.showerror("Permission Error", "Run this tool as Administrator!")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def unblock_websites(urls_to_unblock):
    try:
        with open(HOSTS_PATH, "r") as f:
            lines = f.readlines()
        
        domains_to_unblock = [clean_domain(url) for url in urls_to_unblock]
        
        # Filter out lines that contain any of the domains to unblock
        new_lines = [
            line for line in lines 
            if not any(f" {d}" in line for d in domains_to_unblock)
        ]

        with open(HOSTS_PATH, "w") as f:
            f.writelines(new_lines)
            
        messagebox.showinfo("Unblocked", f"{len(domains_to_unblock)} site(s) unblocked.")
    except PermissionError:
        messagebox.showerror("Permission Error", "Run this tool as Administrator!")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# === WEBSITE REPUTATION CHECK ===
def check_website_reputation():
    win = Toplevel(app)
    win.title("Check Website Reputation")
    win.geometry("500x350")
    win.configure(bg="#1f1f1f")

    tk.Label(win, text="Enter a website URL to check:", bg="#1f1f1f", fg="white").pack(pady=10)
    entry = tk.Entry(win, width=50)
    entry.pack(pady=5)

    def check():
        raw_url = entry.get().strip()
        if not raw_url:
            messagebox.showerror("Input Error", "Please enter a website URL.")
            return
        domain = clean_domain(raw_url)
        try:
            headers = {"x-apikey": VT_API_KEY}
            url = f"https://www.virustotal.com/api/v3/domains/{domain}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()["data"]["attributes"]
                stats = data["last_analysis_stats"]
                categories = data.get("categories", {})
                reputation = data.get("reputation", "N/A")
                tags = ", ".join(data.get("tags", [])) or "None"
                result_text = (
                    f"🔍 Domain: {domain}\n\n"
                    f"🧪 Analysis Stats:\n"
                    f"  - Malicious: {stats.get('malicious', 0)}\n"
                    f"  - Suspicious: {stats.get('suspicious', 0)}\n"
                    f"  - Harmless: {stats.get('harmless', 0)}\n"
                    f"  - Undetected: {stats.get('undetected', 0)}\n\n"
                    f"🏷️ Tags: {tags}\n"
                    f"📊 Reputation Score: {reputation}\n"
                    f"📁 Categories: {json.dumps(categories, indent=2)}"
                )
                messagebox.showinfo("VirusTotal Report", result_text)
            elif response.status_code == 404:
                messagebox.showwarning("Not Found", f"{domain} is not in VirusTotal's database.")
            elif response.status_code == 429:
                messagebox.showwarning("Rate Limit", "VirusTotal rate limit reached. Try again later.")
            else:
                messagebox.showerror("API Error", f"Status Code: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tb.Button(win, text="Check", command=check, bootstyle="info").pack(pady=15)


# === GUI ACTIONS ===
def open_manual_input():
    win = Toplevel(app)
    win.title("Manual URL Entry")
    win.geometry("500x400")
    win.configure(bg="#1f1f1f")
    tk.Label(win, text="Enter URLs:", font=("Arial", 11), bg="#1f1f1f", fg="white").pack(pady=10)
    box = tk.Text(win, height=12, width=60, bg="#2e2e2e", fg="white", insertbackground="white")
    box.pack()

    def block():
        raw = box.get("1.0", tk.END)
        urls = [line.strip() for line in raw.splitlines() if line.strip()]
        if urls:
            start_blocking_with_otp(urls)

    def unblock():
        raw = box.get("1.0", tk.END)
        urls = [line.strip() for line in raw.splitlines() if line.strip()]
        if urls:
            unblock_websites(urls)

    tb.Button(win, text="Block", bootstyle="danger", command=block).pack(pady=8)
    tb.Button(win, text="Unblock", bootstyle="success", command=unblock).pack()


def process_urls_from_file():
    """NEW: Asks user to block or unblock URLs from a file."""
    path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")])
    if not path:
        return

    with open(path, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        messagebox.showinfo("Empty File", "The selected file is empty or contains no valid URLs.")
        return

    # Create a choice window
    choice_win = Toplevel(app)
    choice_win.title("Choose Action")
    choice_win.geometry("350x150")
    choice_win.configure(bg="#1f1f1f")
    tk.Label(choice_win, text="Choose an action for the URLs in the file:", bg="#1f1f1f", fg="white").pack(pady=10)

    def on_block():
        choice_win.destroy()
        start_blocking_with_otp(urls)

    def on_unblock():
        choice_win.destroy()
        unblock_websites(urls)

    tb.Button(choice_win, text="Block Websites", bootstyle="danger", command=on_block).pack(pady=5, fill=X, padx=20)
    tb.Button(choice_win, text="Unblock Websites", bootstyle="success", command=on_unblock).pack(pady=5, fill=X, padx=20)


def open_project_info():
    try:
        os.startfile("info.html")  # Always uses default browser on Windows
    except Exception as e:
        messagebox.showerror("Error", str(e))


def toggle_theme():
    global current_theme
    current_theme = "flatly" if current_theme == "darkly" else "darkly"
    app.style.theme_use(current_theme)


# === GUI LAYOUT ===
tb.Button(app, text="🌓 Toggle Theme", bootstyle="secondary", command=toggle_theme).place(x=370, y=10)
tk.Label(app, text="Malicious Website Blocker Tool", font=("Segoe UI", 20, "bold"), bg="#222831", fg="#00adb5").pack(pady=(25, 10))
tk.Label(app, text=f"Your IP: {get_public_ip()}", font=("Segoe UI", 12), bg="#222831", fg="white").pack(pady=(0, 25))

tb.Button(app, text="📁 Project Info", bootstyle="secondary-outline", command=open_project_info, width=30).pack(pady=10)
tb.Button(app, text="📝 Enter URLs Manually", bootstyle="info", command=open_manual_input, width=30).pack(pady=10)
tb.Button(app, text="📤 Process URL List File", bootstyle="primary", command=process_urls_from_file, width=30).pack(pady=10) # MODIFIED
tb.Button(app, text="🔍 Check Website Reputation", bootstyle="warning", command=check_website_reputation, width=30).pack(pady=10)
tb.Button(app, text="❌ Exit", bootstyle="danger", command=app.quit, width=30).pack(pady=30)

app.mainloop()