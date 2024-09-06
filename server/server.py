from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from flask_cors import CORS
import util
import os
from models import db, bcrypt, login_manager, User, Prediction, create_user, get_user_by_email, check_password, get_user_by_id

app = Flask(__name__, template_folder='../client/templates', static_folder='../client/static')
CORS(app)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Update with your database URI

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

@app.route('/check_login_status', methods=['GET'])
def check_login_status():
    logged_in = current_user.is_authenticated
    return jsonify({'logged_in': logged_in})

@app.route('/get_location_names', methods=['GET'])
def get_location_names():
    locations = util.get_location_names()
    return jsonify({'locations': locations if locations else None})

@app.route('/predict_home_price', methods=['POST'])
def predict_home_price():
    try:
        total_sqft = float(request.form['total_sqft'])
        location = request.form['location']
        bhk = int(request.form['bhk'])
        bath = int(request.form['bath'])

        estimated_price = util.get_estimated_price(location, total_sqft, bhk, bath)
        
        if estimated_price == "Invalid location":
            return jsonify({'error': 'Invalid location. Choose location from dropdown box instead'})
        else:
            return jsonify({'estimated_price': f"{estimated_price} Lakh"})  # Append 'Lakh' to the price

    except ValueError:
        return jsonify({'error': 'Invalid input data. Please check the provided values.'})

@app.route('/save_prediction', methods=['POST'])
@login_required
def save_prediction():
    try:
        user_id = current_user.id
        location = request.form['location']
        sqft = float(request.form['sqft'])
        bhk = int(request.form['bhk'])
        bath = int(request.form['bath'])
        estimated_price = request.form['estimated_price'].strip()  # Ensure no extra spaces
        date_str = request.form['date']
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        new_prediction = Prediction(
            location=location,
            sqft=sqft,
            bhk=bhk,
            bath=bath,
            price=estimated_price,
            user_id=user_id,
            date=date
        )

        db.session.add(new_prediction)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Prediction saved successfully!'})

    except ValueError:
        return jsonify({'error': 'Invalid input data. Please check the provided values.'})

@app.route('/saved_results', methods=['GET'])
@login_required
def saved_results():
    return render_template('saved_results.html')

@app.route('/', methods=['GET'])
def index():
    google_api_key = os.getenv('GOOGLE_API_KEY')
    return render_template('index.html', google_api_key=google_api_key)

@app.route('/get_saved_predictions', methods=['GET'])
@login_required
def get_saved_predictions():
    user_id = current_user.id
    saved_predictions = Prediction.query.filter_by(user_id=user_id).all()
    predictions_list = [{'location': p.location, 'sqft': p.sqft, 'bhk': p.bhk, 'bath': p.bath, 'price': p.price, 'date': p.date.strftime('%Y-%m-%d')} for p in saved_predictions]
    return jsonify({'saved_predictions': predictions_list})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user_by_email(email)
        if user and check_password(user.password, password):
            login_user(user)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        create_user(username, email, password)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    print("Starting Python Flask Server For Home Price Prediction...")
    with app.app_context():
        db.create_all()
        util.load_saved_artifacts()
    # Bind to the port specified by Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
