import os
import time
import json
import hashlib
import smtplib
from email.mime.text import MIMEText

# ================= CONFIG =================
TARGET_DIR = r"C:\Users\sharm\OneDrive\Desktop\target_folder"
BASELINE_FILE = "baseline.json"

EMAIL_SENDER = "test.mail.me103@gmail.com"
EMAIL_PASSWORD = "fktsbvpjvgslajxh"
EMAIL_RECEIVER = "sharmadhanush605@gmail.com"
# ==========================================


# -------- HASH FUNCTION --------
def calculate_hash(file_path):
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest()
    except:
        return None


# -------- CREATE BASELINE --------
def create_baseline():
    baseline = {}

    for file in os.listdir(TARGET_DIR):
        path = os.path.join(TARGET_DIR, file)
        if os.path.isfile(path):
            baseline[path] = calculate_hash(path)

    with open(BASELINE_FILE, "w") as f:
        json.dump(baseline, f, indent=4)

    print("[INFO] Baseline created.")


# -------- LOAD BASELINE --------
def load_baseline():
    if not os.path.exists(BASELINE_FILE):
        create_baseline()

    with open(BASELINE_FILE, "r") as f:
        return json.load(f)


# -------- EMAIL ALERT --------
def send_email_alert(message):
    try:
        msg = MIMEText(message)
        msg["Subject"] = "FIM IDS Alert"
        msg["From"] = "test.mail.me103@gmail.com"
        msg["To"] = "sharmadhanush605@gmail.com"

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("test.mail.me103@gmail.com", "fktsbvpjvgslajxh")
            server.send_message(msg)

        print("[INFO] Email alert sent.")

    except Exception as e:
        print("[ERROR] Email failed:", e)


# -------- MONITOR FUNCTION --------
def monitor():
    baseline = load_baseline()
    print("[INFO] Monitoring started...")

    while True:
        current = {}

        for file in os.listdir(TARGET_DIR):
            path = os.path.join(TARGET_DIR, file)
            if os.path.isfile(path):
                current[path] = calculate_hash(path)

        # Detect changes
        for path in current:
            if path not in baseline:
                msg = f"[ALERT] New file added: {path}"
                print(msg)
                send_email_alert(msg)

            elif baseline[path] != current[path]:
                msg = f"[ALERT] File modified: {path}"
                print(msg)
                send_email_alert(msg)

        for path in baseline:
            if path not in current:
                msg = f"[ALERT] File deleted: {path}"
                print(msg)
                send_email_alert(msg)

        baseline = current

        # Update baseline file automatically
        with open(BASELINE_FILE, "w") as f:
            json.dump(baseline, f, indent=4)

        time.sleep(5)


# -------- MAIN --------
if __name__ == "__main__":
    monitor()