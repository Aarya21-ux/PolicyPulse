import random, datetime
import db

random.seed(7)
EMPS = ["Aarav", "Meera", "Rohan", "Sneha", "Kabir", "Isha"]
CATS = {"meals": 2200, "travel": 9000, "hotel": 8000, "cab": 1500}

db.init_schema()
db.q("DELETE FROM transactions")
for i in range(1, 81):
    cat = random.choice(list(CATS))
    amt = round(random.uniform(0.3, 1.5) * CATS[cat], 0)
    day = datetime.date(2026, 10, random.randint(1, 28))
    db.q("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?)",
         (i, random.choice(EMPS), cat, amt, day,
          random.choice("YYYYN"), random.choice("YYYN")))
# ek duplicate jaan bujhkar
db.q("INSERT INTO transactions SELECT 81, emp, category, amount, txn_date, has_receipt, approved "
     "FROM transactions WHERE id = 1")
print("seeded")
