import json
import os

SESSION_FILE = os.path.join(os.path.expanduser("~"), ".budgetwise_session.json")

def load_session() -> dict:
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            return {}
    return {}

def save_session(username: str, onboarding_completed: bool = True):
    data = {
        "logged_in": True,
        "username": str(username).strip(),
        "onboarding_completed": bool(onboarding_completed)
    }
    try:
        folder = os.path.dirname(SESSION_FILE)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

def clear_session():
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except Exception:
            pass