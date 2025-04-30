from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
DB_NAME = 'money.db'

# Initialize the database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('in', 'out')),
            purpose TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Group transactions by date and calculate summary
def get_grouped_transactions():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date, time, amount, type, purpose FROM transactions ORDER BY date DESC, time DESC")
    transactions = c.fetchall()
    conn.close()

    grouped = defaultdict(list)
    summary = {}

    for date, time, amount, type_, purpose in transactions:
        grouped[date].append({
            "time": time,
            "amount": amount,
            "type": type_,
            "purpose": purpose
        })

    for date, txns in grouped.items():
        income = sum(t["amount"] for t in txns if t["type"] == "in")
        expense = sum(t["amount"] for t in txns if t["type"] == "out")
        summary[date] = {
            "income": income,
            "expense": expense,
            "net": income - expense
        }

    return grouped, summary

@app.route("/")
def index():
    grouped, summary = get_grouped_transactions()
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("index.html", grouped=grouped, summary=summary, today=today)

@app.route("/add", methods=["POST"])
def add_transaction():
    date = request.form["date"]
    amount = float(request.form["amount"])
    type_ = request.form["type"]
    purpose = request.form["purpose"]
    time = datetime.now().strftime("%H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO transactions (date, time, amount, type, purpose) VALUES (?, ?, ?, ?, ?)",
              (date, time, amount, type_, purpose))
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
