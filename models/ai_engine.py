import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline


class StudentAIEngine:
    def __init__(self):
        self.model_file = os.path.join(os.path.dirname(__file__), "expense_classifier.joblib")
        self.model = None
        self.load_or_train_model()

    def load_or_train_model(self):
        if os.path.exists(self.model_file):
            self.model = joblib.load(self.model_file)
        else:
            self.train_and_save_model()

    def train_and_save_model(self):
        training_descriptions = [
            "Coles Supermarket Groceries", "Woolworths Food Purchase", "University Dining Hall",
            "Coffee Shop Macchiato", "Domino's Pizza Delivery", "Subway Sandwich",
            "Campus Bookstore Textbooks", "Library Print Out Fees", "Student Tuition Installment",
            "Course Exam Fee", "University Stationary", "Laptop Repair Lab",
            "Metro Train Fare", "Bus Opal Recharge", "Uber Ride Campus",
            "Tram Ticket City", "Gas Station Petrol Fill", "Car Park Ticket",
            "Target Clothes Shopping", "Amazon Tech Accessories", "Zara Shoes Outlet",
            "Kmart Household Items", "Uniqlo Winter Jacket", "Electronics Store Mouse",
            "Cinema Movie Ticket", "Spotify Music Subscription", "Netflix Monthly",
            "Pub Drinks Social", "Bowling Night", "Concert Ticket Pass",
            "Part-time Job Paycheck", "Tutoring Earnings Deposit", "Cafeteria Wage Payment",
            "Monthly Allowance Transfer", "Scholarship Stipend Payout", "Freelance Work Payment"
        ]

        training_labels = [
            "Food", "Food", "Food", "Food", "Food", "Food",
            "Education", "Education", "Education", "Education", "Education", "Education",
            "Transport", "Transport", "Transport", "Transport", "Transport", "Transport",
            "Shopping", "Shopping", "Shopping", "Shopping", "Shopping", "Shopping",
            "Entertainment", "Entertainment", "Entertainment", "Entertainment", "Entertainment", "Entertainment",
            "Income", "Income", "Income", "Income", "Income", "Income"
        ]

        self.model = make_pipeline(TfidfVectorizer(), MultinomialNB())
        self.model.fit(training_descriptions, training_labels)
        
        joblib.dump(self.model, self.model_file)

    def predict_category(self, description):
        if not description or not self.model:
            return "Shopping"
        return str(self.model.predict([description])[0])
    
    def predict_spending_risk(self, proposed_amount, total_budget, current_expenses, days_remaining):
        effective_remaining = total_budget - current_expenses
        
        if effective_remaining <= 0:
            return 100.0, "🔴 CRITICAL: Budget exhausted! Spending will cause severe debt."

        daily_allowance = effective_remaining / max(days_remaining, 1)
        impact_ratio = proposed_amount / effective_remaining
        
        risk_score = min(100.0, (impact_ratio * 70) + ((proposed_amount / max(daily_allowance, 1)) * 10))

        if risk_score > 70:
            msg = f"⚠️ HIGH RISK ({risk_score:.0f}%): This spend consumes {impact_ratio*100:.1f}% of remaining funds."
        elif risk_score > 40:
            msg = f"🟡 MODERATE RISK ({risk_score:.0f}%): Spending is high relative to daily allowance."
        else:
            msg = f"🟢 LOW RISK ({risk_score:.0f}%): Safe purchase within budget limits."

        return risk_score, msg