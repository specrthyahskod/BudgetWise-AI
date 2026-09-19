import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def generate_synthetic_training_data(n_samples: int = 5000) -> pd.DataFrame:
    """
    Generates realistic student expenditure scenarios factoring:
    - cost: Purchase price (AUD)
    - balance: Current liquid cash (AUD)
    - monthly_burn: 6-month trailing average spend per month (AUD)
    - days_left_in_week: Remaining days in billing/budget cycle (1-7)
    - hourly_wage: Net hourly wage (AUD)
    """
    np.random.seed(42)
    
    cost = np.random.exponential(scale=350, size=n_samples) + 10
    cost = np.clip(cost, 10, 5000)
    
    balance = np.random.gamma(shape=3.0, scale=800, size=n_samples) + 200
    monthly_burn = np.random.normal(loc=1400, scale=350, size=n_samples)
    monthly_burn = np.clip(monthly_burn, 600, 3500)
    
    days_left = np.random.randint(1, 8, size=n_samples)
    wage = np.random.choice([20.50, 22.50, 24.00, 26.50, 30.00], size=n_samples)

    labels = []
    for c, b, mb, dl, w in zip(cost, balance, monthly_burn, days_left, wage):
        rem_balance = b - c
        daily_safespend = rem_balance / dl
        weekly_burn = mb / 4.33
        
        # Label 0: SAFE (2), Label 1: CAUTION (1), Label 2: HIGH RISK (0)
        if rem_balance < 0:
            labels.append(0)  # CANNOT AFFORD 
        elif c < 2000:
            if daily_safespend < 25.0 or rem_balance < (weekly_burn * 0.4):
                labels.append(0)  # HIGH RISK
            elif daily_safespend < 45.0:
                labels.append(1)  # CAUTION
            else:
                labels.append(2)  # SAFE
        else:
            # 6-week capital threshold
            reserve = mb * 1.5
            if rem_balance < reserve:
                labels.append(1 if rem_balance > (reserve * 0.7) else 0)
            else:
                labels.append(2)

    df = pd.DataFrame({
        "cost": cost,
        "balance": balance,
        "monthly_burn": monthly_burn,
        "days_left": days_left,
        "wage": wage,
        "risk_class": labels
    })
    return df

def train_and_export():
    df = generate_synthetic_training_data()
    X = df[["cost", "balance", "monthly_burn", "days_left", "wage"]]
    y = df["risk_class"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print("Affordability Model Evaluation:\n", classification_report(y_test, y_pred))

    os.makedirs("models", exist_ok=True)
    joblib.dump(clf, "models/affordability_model.joblib")
    print("Model artifact successfully saved to models/affordability_model.joblib")

if __name__ == "__main__":
    train_and_export()