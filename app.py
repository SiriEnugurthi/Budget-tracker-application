from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        conn.execute('INSERT INTO Users (u_name, u_pass) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        flash('Registered successfully! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Users WHERE u_name = ? AND u_pass = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['uid']
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid login credentials.')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    uid = session['user_id']

    if request.method == 'POST':
        budget = float(request.form['budget'])
        goal = float(request.form['goal'])
        existing = conn.execute('SELECT * FROM Budget WHERE uid = ?', (uid,)).fetchone()
        if existing:
            conn.execute('UPDATE Budget SET budget = ?, savings_goal = ? WHERE uid = ?', (budget, goal, uid))
        else:
            conn.execute('INSERT INTO Budget (uid, budget, savings_goal) VALUES (?, ?, ?)', (uid, budget, goal))
        conn.commit()
        flash('Budget updated successfully!')

    budget_data = conn.execute('SELECT * FROM Budget WHERE uid = ?', (uid,)).fetchone()
    transactions = conn.execute('SELECT * FROM Transactions WHERE uid = ?', (uid,)).fetchall()
    total_income = sum(t['t_amount'] for t in transactions if t['type'] == 'Income')
    total_expense = sum(t['t_amount'] for t in transactions if t['type'] == 'Expense')
    remaining = (budget_data['budget'] if budget_data else 0) - total_expense
    goal_met = total_income - total_expense >= (budget_data['savings_goal'] if budget_data else 0)
    conn.close()

    return render_template('dashboard.html',
        budget=budget_data['budget'] if budget_data else 0,
        goal=budget_data['savings_goal'] if budget_data else 0,
        income=total_income,
        expense=total_expense,
        remaining=remaining,
        goal_met=goal_met,
        transactions=transactions)

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    uid = session['user_id']
    t_name = request.form['t_name']
    t_amount = float(request.form['t_amount'])
    description = request.form['description']
    date = request.form['date']
    type = request.form['type']
    is_recurring = 1 if request.form.get('recurring') == 'on' else 0

    conn = get_db_connection()
    conn.execute('INSERT INTO Transactions (uid, t_name, t_amount, description, date, type, is_recurring) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (uid, t_name, t_amount, description, date, type, is_recurring))
    conn.commit()
    conn.close()
    flash('Transaction added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)