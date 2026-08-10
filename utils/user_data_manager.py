import json
import os

class UserDataManager:
    def __init__(self, filepath="user_data.json"):
        self.filepath = os.path.join(os.path.dirname(__file__), "..", filepath)
        self.default_data = {
            "username": "Student",
            "hourly_wage": 26.44,
            "fortnight_hours": 48.0,
            "emergency_vault": 300.00,
            "selected_country": "India 🇮🇳",
            "transactions": [],
            "history": []
        }

    def load_data(self):
        if not os.path.exists(self.filepath):
            self.save_data(self.default_data)
            return self.default_data

        try:
            with open(self.filepath, "r") as f:
                return json.load(f)
        except Exception:
            return self.default_data

    def save_data(self, data):
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=4)