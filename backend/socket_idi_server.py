import sys
import io
import socket
import threading
import time
import hashlib
import secrets
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openpyxl import load_workbook

# Force UTF-8 on Windows stdout/stderr to prevent CP1252 character map crashes
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

HOST = "127.0.0.1"
PORT = 9999

SENDER_EMAIL = "mahuyadatta71@gmail.com"
SENDER_APP_PASSWORD = "qzaz lfxk sywu riku"  

USERS_XLSX_FILE = r"C:\Users\Riddhiman\Desktop\BudgetWise-AI\users.xlsx"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDI_SESSIONS_FILE = os.path.join(BASE_DIR, "idi_sessions.json")


def get_current_timestamp():
    return int(time.time())


def apply_layered_sha256(raw_data: str, iterations: int = 1000) -> str:
    hashed = raw_data.encode('utf-8')
    for _ in range(iterations):
        hashed = hashlib.sha256(hashed).digest()
    return hashed.hex()


def load_idi_sessions():
    if os.path.exists(IDI_SESSIONS_FILE):
        try:
            with open(IDI_SESSIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_idi_sessions(sessions):
    with open(IDI_SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=4)


def send_idi_email(recipient_email: str, token: str) -> bool:
    try:
        subject = "BudgetWise AI -- Socket IDI Security Token"
        
        # HTML Email Body
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #0F172A; color: #F8FAFC; padding: 20px;">
                <div style="max-width: 550px; margin: auto; background-color: #1E293B; padding: 25px; border-radius: 12px; border: 1px solid #334155;">
                    <h2 style="color: #60A5FA; margin-top: 0;">BudgetWise AI</h2>
                    <h3 style="color: #F8FAFC;">Password Reset Verification Token</h3>
                    <p style="color: #94A3B8; font-size: 14px;">
                        A password reset request was initiated for your account. Please provide the following 256-bit encrypted session hash code to the administrator or staff intranet portal:
                    </p>
                    
                    <div style="background-color: #0F172A; padding: 15px; border-radius: 8px; border: 1px solid #334155; word-break: break-all; font-family: monospace; font-size: 13px; color: #4ADE80; text-align: center; margin: 20px 0;">
                        {token}
                    </div>

                    <p style="color: #F87171; font-size: 12px; font-weight: bold;">
                        Warning: This security code is valid for exactly 5 minutes (300 seconds).
                    </p>
                    <hr style="border: 0; border-top: 1px solid #334155; margin: 20px 0;">
                    <p style="color: #64748B; font-size: 11px; text-align: center;">
                        If you did not request this reset, please ignore this email.
                    </p>
                </div>
            </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"BudgetWise AI <{SENDER_EMAIL}>"
        msg["To"] = recipient_email
        msg.attach(MIMEText(html_content, "html"))

        # Send via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())

        print(f"[Email Dispatch] IDI Security token successfully mailed to {recipient_email}")
        return True
    except Exception as e:
        print(f"[Email Error] Failed to dispatch email: {e}")
        return False


def generate_idi_token(email: str) -> str:
    timestamp = get_current_timestamp()
    salt = secrets.token_hex(16)
    payload = f"{email}:{timestamp}:{salt}"
    
    hash_chain = apply_layered_sha256(payload, iterations=2048)
    token_256bit = hashlib.sha256(f"{hash_chain}:{salt}".encode('utf-8')).hexdigest()
    
    sessions = load_idi_sessions()
    sessions[token_256bit] = {
        "email": email,
        "created_at": timestamp,
        "expires_at": timestamp + 300,
        "status": "ISSUED",
        "hash_chain": hash_chain
    }
    save_idi_sessions(sessions)
    send_idi_email(email, token_256bit)
    return token_256bit


def update_excel_password(email_or_user: str, new_password: str) -> bool:
    if not os.path.exists(USERS_XLSX_FILE):
        return False
        
    try:
        wb = load_workbook(USERS_XLSX_FILE)
        ws = wb.active
        
        if ws is None:
            wb.close()
            return False

        user_found = False
        max_row = ws.max_row or 0

        for row in range(2, max_row + 1):
            username_cell = ws.cell(row=row, column=1).value
            email_cell = ws.cell(row=row, column=2).value

            username_val = str(username_cell or "").strip()
            email_val = str(email_cell or "").strip()
            
            if email_or_user.lower() in [username_val.lower(), email_val.lower()]:
                ws.cell(row=row, column=3, value=new_password)
                user_found = True
                break
                
        if user_found:
            wb.save(USERS_XLSX_FILE)
            wb.close()
            return True

        wb.close()
    except Exception as e:
        print(f"Error updating Excel: {e}")
        return False
        
    return False


def handle_socket_client(client_socket, address):
    try:
        raw_message = client_socket.recv(4096).decode('utf-8')
        if not raw_message:
            client_socket.close()
            return
            
        packet = json.loads(raw_message)
        action = packet.get("action")
        response = {"status": "ERROR", "message": "Invalid Request"}
        
        if action == "REQUEST_IDI_LINK":
            email = packet.get("email")
            if email:
                token = generate_idi_token(email)
                response = {
                    "status": "SUCCESS",
                    "action": "IDI_DISPATCHED",
                    "token_preview": f"{token[:8]}...{token[-8:]}",
                    "expires_in": 300,
                    "message": f"IDI Challenge token dispatched to {email}"
                }
                
        elif action == "VERIFY_AND_RESET":
            token = packet.get("token")
            new_password = packet.get("new_password")
            
            sessions = load_idi_sessions()
            if token in sessions:
                session = sessions[token]
                current_time = get_current_timestamp()
                
                if current_time > session["expires_at"]:
                    session["status"] = "EXPIRED"
                    save_idi_sessions(sessions)
                    response = {"status": "FAILED", "message": "IDI Session token expired (>5 mins)"}
                elif session["status"] == "USED":
                    response = {"status": "FAILED", "message": "IDI Session token already consumed"}
                else:
                    success = update_excel_password(session["email"], new_password)
                    
                    if success:
                        session["status"] = "USED"
                        save_idi_sessions(sessions)
                        response = {
                            "status": "SUCCESS",
                            "action": "PASSWORD_RESET_COMPLETE",
                            "email": session["email"],
                            "message": "Intranet Socket IDI verification passed. Password updated in users.xlsx."
                        }
                    else:
                        response = {"status": "FAILED", "message": "Account email/user not found in users.xlsx"}
            else:
                response = {"status": "FAILED", "message": "Invalid IDI Token"}

        client_socket.send(json.dumps(response).encode('utf-8'))
    except Exception as e:
        err_res = {"status": "ERROR", "message": str(e)}
        client_socket.send(json.dumps(err_res).encode('utf-8'))
    finally:
        client_socket.close()


def start_socket_idi_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    
    print(f"[Socket IDI Daemon Active] Listening on {HOST}:{PORT}")
    
    while True:
        client_sock, addr = server.accept()
        thread = threading.Thread(target=handle_socket_client, args=(client_sock, addr))
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    start_socket_idi_server()