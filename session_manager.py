import json
import os

SESSION_FILE = os.path.join(os.path.expanduser("~"), ".budgetwise_session.json")

def load_session() -> dict:
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_session(username: str, onboarding_completed: bool = True):
    data = {
        "logged_in": True,
        "username": username,
        "onboarding_completed": onboarding_completed
    }
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass

def clear_session():
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except Exception:
            pass