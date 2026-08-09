import os
import random
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

def generate_massive_financial_dataset():
    category_terms = {
        "Food": [
            "Coles", "Woolworths", "Woolies", "ALDI", "IGA", "Harris Farm", "Costco Groceries",
            "McDonalds", "Hungry Jacks", "KFC", "Domino's Pizza", "Subway", "Guzman y Gomez", "GYG",
            "Grill'd", "Sushi Hub", "Chatime", "Gong Cha", "Sharetea", "Starbucks", "7-Eleven Food",
            "Campus Cafe", "Uni Dining Hall", "Coffee Shop", "Bakery", "Kebab Shop", "Noodle Bar",
            "Restaurant", "Diner", "Takeaway", "UberEats", "DoorDash", "Menulog", "Deliveroo",
            "Supermarket", "Fruit Market", "Butcher", "Deli", "Pizzeria", "Burger Bar", "Espresso"
        ],
        "Education": [
            "USYD Bookstore", "UniMelb Student Union", "Monash Press", "UNSW Textbooks",
            "Library Print", "Tuition Fee", "Student Services", "Course Installment", "Exam Fee",
            "Stationery", "Lab Access Fee", "Laptop Repair", "Assignment Printout", "Textbook Purchase",
            "Udemy Course", "Coursera Certificate", "Chegg Study", "Quizlet Plus", "Notion Student"
        ],
        "Transport": [
            "Opal Recharge", "Myki Top Up", "Go Card Transit", "Metro Train", "Bus Fare", "Tram Ticket",
            "Uber Ride", "DiDi Taxi", "Ola Cabs", "13CABS", "Gas Station", "Petrol Fill", "Shell Fuel",
            "BP Connect", "7-Eleven Fuel", "Caltex", "Ampol", "Car Park", "Parking Meter", "Wilson Parking"
        ],
        "Shopping": [
            "Target", "Kmart", "Big W", "IKEA", "Zara", "H&M", "Uniqlo", "Cotton On", "Myer", "David Jones",
            "Amazon AU", "eBay", "Catch AU", "JB Hi-Fi", "The Good Guys", "Harvey Norman", "Apple Store",
            "Priceline Pharmacy", "Chemist Warehouse", "MECCA", "Sephora", "Daiso", "Miniso"
        ],
        "Entertainment": [
            "Event Cinemas", "HOYTS Cinema", "Palace Cinema", "IMAX Ticket", "Spotify", "Netflix",
            "Stan Australia", "Binge AU", "Disney Plus", "Amazon Prime Video", "Apple Music", "YouTube Premium",
            "Steam Games", "PlayStation Network", "Xbox Game Pass", "Nintendo eShop", "Twitch Sub"
        ],
        "Income": [
            "Part Time Paycheck", "Casual Wage", "Tutoring Earnings", "Salary Deposit", "Payroll Transfer",
            "Scholarship Stipend", "AAS Grant", "Allowance", "Parents Transfer", "Freelance Payment",
            "Tax Refund ATO", "Centrelink Payment", "Youth Allowance", "Austudy", "Etsy Earnings"
        ]
    }

    prefix_templates = ["", "Store ", "Online ", "App ", "Express ", "Local ", "Direct Debit ", "POS "]
    suffix_templates = ["", " AUD", " Payment", " Charge", " Transaction", " Transfer", " Purchase", " Sydney"]

    descriptions = []
    labels = []

    for category, terms in category_terms.items():
        for term in terms:
            descriptions.append(term)
            labels.append(category)

            descriptions.append(term.lower())
            labels.append(category)

            descriptions.append(term.upper())
            labels.append(category)

            for _ in range(4):
                pre = random.choice(prefix_templates)
                suf = random.choice(suffix_templates)
                aug_text = f"{pre}{term}{suf}".strip()
                descriptions.append(aug_text)
                labels.append(category)

    return descriptions, labels


def train_and_evaluate_model():
    descriptions, labels = generate_massive_financial_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        descriptions, labels, test_size=0.20, random_state=42, stratify=labels
    )

    model = make_pipeline(
        TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 5),
            sublinear_tf=True
        ),
        ComplementNB(alpha=0.1)
    )
    
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred) * 100

    print("=" * 60)
    print("🤖 BUDGETWISE AI - MASSIVE DATASET TRAINING RESULTS")
    print("=" * 60)
    print(f"Total Dataset Generated: {len(descriptions)} samples")
    print(f"Training Set Size:       {len(X_train)} samples")
    print(f"Testing Set Size:        {len(X_test)} samples")
    print(f"Model Accuracy:          {accuracy:.2f}%")
    print("=" * 60)
    
    print("\n📊 Detailed Classification Report:\n")
    print(classification_report(y_test, y_pred, zero_division=0))

    model_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "expense_classifier.joblib")
    
    joblib.dump(model, model_path)
    print(f"✅ Trained model saved to: {model_path}\n")


if __name__ == "__main__":
    train_and_evaluate_model()