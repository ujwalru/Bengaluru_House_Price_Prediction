from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, LoginManager

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'login'  # Redirects to login page if user is not logged in

@login_manager.user_loader
def load_user(user_id):
    """Load the user for the Flask-Login session."""
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """User model for user authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # Relationship with Prediction
    predictions = db.relationship('Prediction', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Prediction(db.Model):
    """Prediction model to store user's price predictions."""
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    sqft = db.Column(db.Float, nullable=False)
    bhk = db.Column(db.Integer, nullable=False)
    bath = db.Column(db.Integer, nullable=False)
    price = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Prediction('{self.location}', {self.sqft} sqft, {self.bhk} BHK, {self.bath} Bath, Price: {self.price})"

# Helper functions

def create_user(username, email, password):
    """
    Create a new user with a hashed password and add them to the database.
    """
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')  # Hash the password
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

def get_user_by_email(email):
    """
    Retrieve a user by their email.
    """
    return User.query.filter_by(email=email).first()

def get_user_by_id(user_id):
    """
    Retrieve a user by their ID.
    """
    return User.query.get(user_id)

def check_password(hashed_password, password):
    """
    Check if the provided password matches the hashed password.
    """
    return bcrypt.check_password_hash(hashed_password, password)
