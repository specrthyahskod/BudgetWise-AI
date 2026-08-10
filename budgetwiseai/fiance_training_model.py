import os
import random
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


def generate_financial_dataset():
    category_terms = {
        "Food": [
            "Coles", "Woolworths", "Supermarket", "ALDI", "IGA", "Groceries",
            "McDonalds", "Hungry Jacks", "KFC", "Dominos Pizza", "Subway", "Burger Bar",
            "Grilld", "Sushi Hub", "Chatime", "Starbucks", "7-Eleven Food",
            "Campus Cafe", "Dining Hall", "Coffee Shop", "Bakery", "Kebab Shop", "Noodle Bar",
            "Restaurant", "Diner", "Takeaway", "UberEats", "DoorDash", "Menulog",
            "Fruit Market", "Pizzeria", "Bubble Tea", "Ramen", "Bakery Croissant"
        ],
        "Education": [
            "Campus Bookstore", "Student Union", "University Press", "Textbooks",
            "Library Print", "Tuition Fee", "Student Services", "Course Installment", "Exam Fee",
            "Stationery", "Lab Access Fee", "Laptop Repair", "Assignment Printout", "Textbook Purchase",
            "Udemy Course", "Coursera Certificate", "Chegg Study", "Quizlet Plus", "Notion Student",
            "Grammarly", "GitHub Student", "LaTeX Subscription", "Calculators Store", "Graduation Gown",
            "Academic Journal", "Research Paper PDF", "Overleaf Pro", "Student ID Replacement"
        ],
        "Transport": [
            "Transit Card Top Up", "Metro Train", "Bus Fare", "Tram Ticket",
            "Uber Ride", "DiDi Taxi", "Ola Cabs", "Gas Station", "Petrol Fill", "Shell Fuel",
            "BP Connect", "7-Eleven Fuel", "Caltex", "Ampol", "Car Park", "Parking Meter", "Wilson Parking",
            "Bike Repair", "Airport Express", "State Transit", "Train Pass Monthly"
        ],
        "Shopping": [
            "Target", "Kmart", "Big W", "IKEA", "Zara", "H&M", "Uniqlo", "Cotton On", "Myer",
            "Amazon AU", "eBay", "JB Hi-Fi", "Harvey Norman", "Apple Store",
            "Priceline Pharmacy", "Chemist Warehouse", "Sephora", "Daiso", "Miniso", "Foot Locker",
            "Nike Store", "Adidas Outlet", "Electronics", "Homewares", "Fashion Outlet", "Sneakers"
        ],
        "Entertainment": [
            "Event Cinemas", "HOYTS Cinema", "IMAX Ticket", "Spotify", "Netflix",
            "Stan", "Binge", "Disney Plus", "Amazon Prime Video", "Apple Music", "YouTube Premium",
            "Steam Games", "PlayStation Network", "Xbox Game Pass", "Nintendo eShop", "Twitch Sub",
            "Pub Drinks", "Bar Tab", "Bowling Night", "Escape Room", "Concert Ticket",
            "Gym Membership", "Anytime Fitness", "F45 Training", "Karaoke Room"
        ],
        "Income": [
            "Part Time Paycheck", "Casual Wage", "Tutoring Earnings", "Salary Deposit", "Payroll Transfer",
            "Scholarship Stipend", "Grant", "Allowance", "Parents Transfer", "Freelance Payment",
            "Tax Refund", "Government Support", "Youth Allowance", "Etsy Earnings", "Shift Pay"
        ]
    }

    prefix_templates = ["", "Store ", "Online ", "App ", "Express ", "Local ", "Direct Debit "]
    suffix_templates = ["", " AUD", " Payment", " Charge", " Transaction", " Transfer", " Purchase"]

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

            for i in range(4):
                pre = random.choice(prefix_templates)
                suf = random.choice(suffix_templates)
                text = f"{pre}{term}{suf}".strip()
                descriptions.append(text)
                labels.append(category)

    return descriptions, labels


def train_and_save_model():
    descriptions, labels = generate_financial_dataset()

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
    acc = accuracy_score(y_test, y_pred) * 100

    print(f"Dataset Size: {len(descriptions)}")
    print(f"Training Accuracy: {acc:.2f}%")
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred, zero_division=0))

    model_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(model_dir, exist_ok=True)
    file_path = os.path.join(model_dir, "expense_classifier.joblib")

    joblib.dump(model, file_path)
    print(f"Saved model to: {file_path}")


if __name__ == "__main__":
    train_and_save_model()