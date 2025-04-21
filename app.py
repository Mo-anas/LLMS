from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson.objectid import ObjectId
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MongoDB Configuration
client = MongoClient("mongodb://localhost:27017/")
db = client["language_center"]

# Collections
users = db["users"]
members = db["members"]
languages = db["languages"]
member_languages = db["member_languages"]
payments = db["payments"]

# Flask-Login User Class
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]
        self.password = user_data["password"]

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    user_data = users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

# Custom template filter
@app.template_filter('formatCurrency')
def format_currency(value):
    return f"₹{value:,.2f}"

# Health Check Route
@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "App is running!"})

# Routes
@app.route('/')
@login_required
def dashboard():
    total_members = members.count_documents({})
    recent_members = list(members.find().sort("start_date", -1).limit(5))
    
    recent_payments = list(payments.aggregate([
        {"$sort": {"date": -1}},
        {"$limit": 5},
        {"$lookup": {
            "from": "members",
            "localField": "member_id",
            "foreignField": "_id",
            "as": "member"
        }},
        {"$unwind": "$member"},
        {"$project": {
            "amount": 1,
            "date": 1,
            "method": 1,
            "name": "$member.name"
        }}
    ]))
    
    return render_template('dashboard.html', 
                         total_members=total_members,
                         recent_members=recent_members,
                         recent_payments=recent_payments)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = users.find_one({"username": username})
        
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/members')
@login_required
def view_members():
    all_members = list(members.find())
    return render_template('view_members.html', members=all_members)

@app.route('/members/add', methods=['GET', 'POST'])
@login_required
def add_member():
    if request.method == 'POST':
        try:
            new_member = {
                "name": request.form['name'],
                "email": request.form['email'],
                "phone": request.form['phone'],
                "dob": datetime.strptime(request.form['dob'], '%Y-%m-%d'),
                "address": request.form['address'],
                "start_date": datetime.utcnow(),
                "languages": [],
                "payments": []
            }
            members.insert_one(new_member)
            flash('Member added successfully', 'success')
            return redirect(url_for('view_members'))
        except Exception as e:
            flash(f'Error adding member: {str(e)}', 'error')
    
    return render_template('add_member.html')

@app.route('/members/<member_id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def member_details(member_id):
    member = members.find_one({"_id": ObjectId(member_id)})
    
    if request.method == 'DELETE':
        try:
            members.delete_one({"_id": ObjectId(member_id)})
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    if request.method == 'POST':
        try:
            members.update_one(
                {"_id": ObjectId(member_id)},
                {"$set": {
                    "name": request.form['name'],
                    "email": request.form['email'],
                    "phone": request.form['phone'],
                    "dob": datetime.strptime(request.form['dob'], '%Y-%m-%d'),
                    "address": request.form['address']
                }}
            )
            flash('Member details updated successfully', 'success')
        except Exception as e:
            flash(f'Error updating member: {str(e)}', 'error')
    
    enrolled_languages = list(member_languages.find({"member_id": ObjectId(member_id)}))
    payment_history = list(payments.find({"member_id": ObjectId(member_id)}))
    
    return render_template('member_details.html', 
                         member=member,
                         languages=enrolled_languages,
                         payments=payment_history)

@app.route('/members/<member_id>/languages/<language_id>', methods=['DELETE'])
@login_required
def delete_member_language(member_id, language_id):
    try:
        member_languages.delete_one({
            "member_id": ObjectId(member_id),
            "language_id": ObjectId(language_id)
        })
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/members/<member_id>/add_language', methods=['GET', 'POST'])
@login_required
def add_language(member_id):
    member = members.find_one({"_id": ObjectId(member_id)})
    
    if request.method == 'POST':
        try:
            language_id = request.form['language_id']
            level = request.form['level']
            plan = request.form['plan']
            duration = int(request.form['duration'])
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
            amount = float(request.form['amount'])
            
            new_enrollment = {
                "member_id": ObjectId(member_id),
                "language_id": ObjectId(language_id),
                "level": level,
                "plan": plan,
                "duration": duration,
                "start_date": start_date,
                "end_date": end_date,
                "amount": amount,
                "payment_status": "Pending"
            }
            member_languages.insert_one(new_enrollment)
            
            flash('Language added successfully', 'success')
            return redirect(url_for('member_details', member_id=member_id))
        except Exception as e:
            flash(f'Error adding language: {str(e)}', 'error')
    
    all_languages = list(languages.find())
    return render_template('add_language.html', member=member, languages=all_languages)

@app.route('/members/<member_id>/add_payment', methods=['GET', 'POST'])
@login_required
def add_payment(member_id):
    member = members.find_one({"_id": ObjectId(member_id)})
    
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            method = request.form['method']
            date = datetime.strptime(request.form['date'], '%Y-%m-%d')
            language_id = request.form.get('language_id')
            notes = request.form.get('notes')
            
            new_payment = {
                "member_id": ObjectId(member_id),
                "amount": amount,
                "method": method,
                "date": date,
                "for_language": ObjectId(language_id) if language_id else None,
                "notes": notes
            }
            payments.insert_one(new_payment)
            
            if language_id:
                member_languages.update_one(
                    {
                        "member_id": ObjectId(member_id),
                        "language_id": ObjectId(language_id)
                    },
                    {"$set": {"payment_status": "Paid"}}
                )
            
            flash('Payment recorded successfully', 'success')
            return redirect(url_for('member_details', member_id=member_id))
        except Exception as e:
            flash(f'Error recording payment: {str(e)}', 'error')
    
    enrolled_languages = list(member_languages.find({"member_id": ObjectId(member_id)}))
    return render_template('payments.html', member=member, languages=enrolled_languages)

@app.route('/languages')
@login_required
def manage_languages():
    all_languages = list(languages.find())
    return render_template('languages.html', languages=all_languages)

@app.route('/reports')
@login_required
def reports():
    try:
        enrollments = list(member_languages.aggregate([
            {"$lookup": {
                "from": "members",
                "localField": "member_id",
                "foreignField": "_id",
                "as": "member"
            }},
            {"$lookup": {
                "from": "languages",
                "localField": "language_id",
                "foreignField": "_id",
                "as": "language"
            }},
            {"$unwind": "$member"},
            {"$unwind": "$language"},
            {"$project": {
                "member_id": "$member._id",
                "member_name": "$member.name",
                "language_name": "$language.name",
                "level": 1,
                "start_date": 1,
                "end_date": 1,
                "amount": 1,
                "payment_status": 1
            }}
        ])) or []

        total_revenue = 0
        total_result = list(member_languages.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]))
        if total_result:
            total_revenue = total_result[0].get("total", 0)

        paid_revenue = 0
        paid_result = list(member_languages.aggregate([
            {"$match": {"payment_status": "Paid"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]))
        if paid_result:
            paid_revenue = paid_result[0].get("total", 0)

        pending_revenue = max(total_revenue - paid_revenue, 0)

        monthly_revenue = list(payments.aggregate([
            {"$group": {
                "_id": {
                    "year": {"$year": "$date"},
                    "month": {"$month": "$date"}
                },
                "total": {"$sum": "$amount"}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ])) or []

        return render_template('reports.html',
                            enrollments=enrollments,
                            total_revenue=total_revenue,
                            paid_revenue=paid_revenue,
                            pending_revenue=pending_revenue,
                            monthly_revenue=monthly_revenue)

    except Exception as e:
        flash(f"Error generating reports: {str(e)}", "error")
        return render_template('reports.html',
                            enrollments=[],
                            total_revenue=0,
                            paid_revenue=0,
                            pending_revenue=0,
                            monthly_revenue=[])

def initialize_database():
    if users.count_documents({}) == 0:
        users.insert_one({
            "username": "admin",
            "password": generate_password_hash("admin123")
        })
    
    if languages.count_documents({}) == 0:
        indian_languages = [
            {"language_id": 101, "name": "Hindi", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1000},
            {"language_id": 102, "name": "Bengali", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1000},
            {"language_id": 103, "name": "Tamil", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1000},
            {"language_id": 104, "name": "Telugu", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1000},
            {"language_id": 105, "name": "Marathi", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1000},
            {"language_id": 106, "name": "Gujarati", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1000},
            {"language_id": 107, "name": "Malayalam", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1000},
            {"language_id": 108, "name": "Kannada", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1000},
            {"language_id": 109, "name": "Punjabi", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1000}
        ]
        
        international_languages = [
            {"language_id": 201, "name": "English", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1500},
            {"language_id": 202, "name": "Spanish", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1500},
            {"language_id": 203, "name": "French", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1500},
            {"language_id": 204, "name": "German", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1500},
            {"language_id": 205, "name": "Japanese", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 2000},
            {"language_id": 206, "name": "Chinese", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 2000},
            {"language_id": 207, "name": "Russian", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1500},
            {"language_id": 208, "name": "Arabic", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1500},
            {"language_id": 209, "name": "Portuguese", "levels": ["Beginner", "Intermediate", "Advanced"], "durations": [3, 6, 9], "base_price": 1500}
        ]
        
        languages.insert_many(indian_languages + international_languages)

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
