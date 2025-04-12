from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
import bcrypt
from bson.objectid import ObjectId
import os
from functools import wraps

app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
app.config["MONGO_URI"] = "mongodb://localhost:27017/language_membership"
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session lifetime

mongo = PyMongo(app)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Initialize database with sample data
def initialize_db():
    if mongo.db.users.count_documents({}) == 0:
        hashed_pw = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        mongo.db.users.insert_one({
            'username': 'admin',
            'password': hashed_pw,
            'role': 'admin',
            'created_at': datetime.now()
        })
    
    if mongo.db.languages.count_documents({}) == 0:
        languages = [
            # Indian Languages (IDs 100-109)
            {'language_id': 100, 'name': 'Hindi', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 500, 'created_at': datetime.now()},
            {'language_id': 101, 'name': 'Tamil', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 600, 'created_at': datetime.now()},
            {'language_id': 102, 'name': 'Telugu', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 550, 'created_at': datetime.now()},
            {'language_id': 103, 'name': 'Marathi', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 500, 'created_at': datetime.now()},
            {'language_id': 104, 'name': 'Bengali', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 600, 'created_at': datetime.now()},
            {'language_id': 105, 'name': 'Gujarati', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 550, 'created_at': datetime.now()},
            {'language_id': 106, 'name': 'Kannada', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 600, 'created_at': datetime.now()},
            {'language_id': 107, 'name': 'Odia', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 500, 'created_at': datetime.now()},
            {'language_id': 108, 'name': 'Punjabi', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 550, 'created_at': datetime.now()},
            {'language_id': 109, 'name': 'Malayalam', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 600, 'created_at': datetime.now()},
            
            # International Languages (IDs 110+)
            {'language_id': 110, 'name': 'Arabic', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 700, 'created_at': datetime.now()},
            {'language_id': 111, 'name': 'Russian', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 750, 'created_at': datetime.now()},
            {'language_id': 112, 'name': 'Japanese', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 800, 'created_at': datetime.now()},
            {'language_id': 113, 'name': 'Turkish', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 650, 'created_at': datetime.now()},
            {'language_id': 114, 'name': 'Malay/Indonesian', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 600, 'created_at': datetime.now()},
            {'language_id': 115, 'name': 'French', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 700, 'created_at': datetime.now()},
            {'language_id': 116, 'name': 'Italian', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 700, 'created_at': datetime.now()},
            {'language_id': 117, 'name': 'German', 'levels': ['Beginner', 'Intermediate', 'Advanced'], 
             'durations': [1, 3, 6], 'base_price': 700, 'created_at': datetime.now()}
        ]
        mongo.db.languages.insert_many(languages)

# Format currency filter
@app.template_filter('formatCurrency')
def format_currency(value):
    return f"₹{value:,.2f}"

# Routes
@app.route('/')
@login_required
def home():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'username': request.form['username']})
        
        if login_user and bcrypt.checkpw(request.form['password'].encode('utf-8'), login_user['password']):
            session['username'] = request.form['username']
            session['role'] = login_user.get('role', 'user')
            session.permanent = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid username/password combination', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    total_members = mongo.db.members.count_documents({})
    recent_members = mongo.db.members.find().sort('member_id', -1).limit(5)
    
    recent_payments = list(mongo.db.members.aggregate([
        {'$unwind': '$payments'},
        {'$sort': {'payments.date': -1}},
        {'$limit': 5},
        {'$project': {
            'member_id': 1,
            'name': 1,
            'amount': '$payments.amount',
            'date': '$payments.date',
            'method': '$payments.method'
        }}
    ]))
    
    return render_template('dashboard.html', 
                         total_members=total_members,
                         recent_members=recent_members,
                         recent_payments=recent_payments)

@app.route('/members')
@login_required
def view_members():
    members = mongo.db.members.find().sort('member_id', 1)
    return render_template('view_members.html', members=members)

@app.route('/add_member', methods=['GET', 'POST'])
@login_required
def add_member():
    if request.method == 'POST':
        members = mongo.db.members
        last_member = members.find_one(sort=[("member_id", -1)])
        new_id = last_member['member_id'] + 1 if last_member else 1
        
        member_data = {
            'member_id': new_id,
            'name': request.form['name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'dob': datetime.strptime(request.form['dob'], '%Y-%m-%d'),
            'address': request.form['address'],
            'start_date': datetime.now(),
            'languages': [],
            'payments': [],
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        members.insert_one(member_data)
        flash(f'Member {new_id} added successfully!', 'success')
        return redirect(url_for('member_details', member_id=new_id))
    
    return render_template('add_member.html')

@app.route('/member/<int:member_id>', methods=['GET', 'POST'])
@login_required
def member_details(member_id):
    member = mongo.db.members.find_one({'member_id': member_id})
    if not member:
        flash('Member not found', 'danger')
        return redirect(url_for('view_members'))
    
    if request.method == 'POST':
        update_data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'dob': datetime.strptime(request.form['dob'], '%Y-%m-%d'),
            'address': request.form['address'],
            'updated_at': datetime.now()
        }
        
        mongo.db.members.update_one(
            {'member_id': member_id},
            {'$set': update_data}
        )
        flash('Member details updated successfully!', 'success')
        return redirect(url_for('member_details', member_id=member_id))
    
    return render_template('member_details.html', member=member)

@app.route('/member/<int:member_id>/add_language', methods=['GET', 'POST'])
@login_required
def add_language(member_id):
    member = mongo.db.members.find_one({'member_id': member_id})
    if not member:
        flash('Member not found', 'danger')
        return redirect(url_for('view_members'))
    
    languages = list(mongo.db.languages.find())
    
    if request.method == 'POST':
        language_id = int(request.form['language_id'])
        language = mongo.db.languages.find_one({'language_id': language_id})
        
        if not language:
            flash('Invalid language selected', 'danger')
            return redirect(url_for('add_language', member_id=member_id))
        
        base_price = language['base_price']
        duration = int(request.form['duration'])
        level = request.form['level']
        
        amount = base_price * duration
        if level == 'Intermediate':
            amount *= 1.2
        elif level == 'Advanced':
            amount *= 1.5
        
        new_language = {
            'language_id': language_id,
            'name': language['name'],
            'level': level,
            'duration': duration,
            'start_date': datetime.strptime(request.form['start_date'], '%Y-%m-%d'),
            'amount': amount,
            'added_at': datetime.now()
        }
        
        mongo.db.members.update_one(
            {'member_id': member_id},
            {'$push': {'languages': new_language}}
        )
        
        flash(f'{language["name"]} added to member successfully!', 'success')
        return redirect(url_for('member_details', member_id=member_id))
    
    return render_template('add_language.html', 
                         member=member, 
                         languages=languages)

@app.route('/member/<int:member_id>/add_payment', methods=['GET', 'POST'])
@login_required
def add_payment(member_id):
    member = mongo.db.members.find_one({'member_id': member_id})
    if not member:
        flash('Member not found', 'danger')
        return redirect(url_for('view_members'))
    
    if request.method == 'POST':
        last_payment = mongo.db.members.aggregate([
            {'$unwind': '$payments'},
            {'$sort': {'payments.payment_id': -1}},
            {'$limit': 1},
            {'$project': {'payment_id': '$payments.payment_id'}}
        ])
        
        last_payment_id = next(last_payment, {}).get('payment_id', 0)
        new_payment_id = last_payment_id + 1
        
        payment_data = {
            'payment_id': new_payment_id,
            'amount': float(request.form['amount']),
            'method': request.form['method'],
            'date': datetime.strptime(request.form['date'], '%Y-%m-%d'),
            'for_language': int(request.form['language_id']) if request.form['language_id'] else None,
            'notes': request.form.get('notes', ''),
            'recorded_at': datetime.now()
        }
        
        mongo.db.members.update_one(
            {'member_id': member_id},
            {'$push': {'payments': payment_data}}
        )
        
        flash('Payment recorded successfully!', 'success')
        return redirect(url_for('member_details', member_id=member_id))
    
    return render_template('payments.html', member=member)

@app.route('/languages')
@login_required
def manage_languages():
    languages = mongo.db.languages.find().sort('name', 1)
    return render_template('languages.html', languages=languages)

@app.route('/reports')
@login_required
def reports():
    language_popularity = list(mongo.db.members.aggregate([
        {'$unwind': '$languages'},
        {'$group': {
            '_id': '$languages.name',
            'count': {'$sum': 1},
            'total_revenue': {'$sum': '$languages.amount'}
        }},
        {'$sort': {'count': -1}}
    ]))
    
    monthly_revenue = list(mongo.db.members.aggregate([
        {'$unwind': '$payments'},
        {'$project': {
            'year': {'$year': '$payments.date'},
            'month': {'$month': '$payments.date'},
            'amount': '$payments.amount'
        }},
        {'$group': {
            '_id': {'year': '$year', 'month': '$month'},
            'total': {'$sum': '$amount'}
        }},
        {'$sort': {'_id.year': 1, '_id.month': 1}},
        {'$limit': 12}
    ]))
    
    return render_template('reports.html',
                         language_popularity=language_popularity,
                         monthly_revenue=monthly_revenue)

# API Endpoints
@app.route('/api/languages')
@login_required
def api_languages():
    languages = list(mongo.db.languages.find({}, {'_id': 0}))
    return jsonify(languages)

@app.route('/api/member/<int:member_id>/delete', methods=['POST'])
@login_required
def api_delete_member(member_id):
    result = mongo.db.members.delete_one({'member_id': member_id})
    if result.deleted_count > 0:
        return jsonify({'success': True, 'message': 'Member deleted successfully'})
    return jsonify({'success': False, 'message': 'Member not found'}), 404

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        initialize_db()
    app.run(debug=True)