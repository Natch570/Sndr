from flask import Flask, render_template, request, redirect, url_for, flash, g, jsonify, send_from_directory, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
from datetime import datetime, timedelta
import os
import uuid
import re
import secrets
from email_validator import validate_email, EmailNotValidError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import jinja2
import json
from pywebpush import webpush, WebPushException

# Only import flask_ngrok in development environment, not on Render
is_render = os.path.exists('/opt/render')
if not is_render:
    try:
        from flask_ngrok import run_with_ngrok
    except ImportError:
        # If flask_ngrok is not installed, define a dummy function
        def run_with_ngrok(app):
            pass
else:
    # Define dummy function if running on Render
    def run_with_ngrok(app):
        pass

# Configuration
# Check if we're running on Render
if os.path.exists('/opt/render'):
    # Use Render.com specific paths
    template_dir = '/opt/render/project/src/templates'
    static_dir = '/opt/render/project/src/static'
    
    # Try to create template and static directories if they don't exist
    if not os.path.exists(template_dir):
        try:
            os.makedirs(template_dir, exist_ok=True)
            print(f"Created template directory: {template_dir}")
            
            # Create a base.html template file with proper styling
            with open(os.path.join(template_dir, 'base.html'), 'w') as f:
                f.write('''
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{% block title %}Sndr - Anonymous Messaging{% endblock %}</title>
                    
                    <!-- Bootstrap CSS -->
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
                    
                    <!-- Font Awesome -->
                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
                    
                    <style>
                        :root {
                            --primary-color: #ff69b4;
                            --primary-dark: #d65a9a;
                            --primary-light: #ffb6c1;
                            --secondary-color: #f9f2f4;
                        }
                        
                        body {
                            font-family: 'Arial', sans-serif;
                            background-color: var(--secondary-color);
                            color: #333;
                        }
                        
                        .navbar {
                            background-color: var(--primary-color);
                        }
                        
                        .navbar-brand {
                            font-weight: bold;
                            color: white !important;
                        }
                        
                        .nav-link {
                            color: white !important;
                            position: relative;
                            transition: all 0.3s ease;
                        }
                        
                        .nav-link:hover {
                            color: white !important;
                            transform: translateY(-2px);
                        }
                        
                        .nav-link::after {
                            content: '';
                            position: absolute;
                            width: 0;
                            height: 2px;
                            bottom: 0;
                            left: 0;
                            background-color: white;
                            transition: width 0.3s ease;
                        }
                        
                        .nav-link:hover::after {
                            width: 100%;
                        }
                        
                        .btn-primary {
                            background-color: var(--primary-color);
                            border-color: var(--primary-color);
                        }
                        
                        .btn-primary:hover {
                            background-color: var(--primary-dark);
                            border-color: var(--primary-dark);
                        }
                        
                        .auth-card {
                            border-radius: 15px;
                            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
                            border: none;
                        }
                        
                        .auth-header {
                            color: var(--primary-color);
                        }
                        
                        .auth-form .form-control:focus {
                            border-color: var(--primary-color);
                            box-shadow: 0 0 0 0.25rem rgba(255, 105, 180, 0.25);
                        }
                        
                        .auth-links a {
                            color: var(--primary-color);
                            text-decoration: none;
                            transition: all 0.3s ease;
                        }
                        
                        .auth-links a:hover {
                            color: var(--primary-dark);
                            text-decoration: underline;
                        }
                        
                        .text-primary {
                            color: var(--primary-color) !important;
                        }
                    </style>
                    
                    {% block extra_css %}{% endblock %}
                </head>
                <body>
                    <nav class="navbar navbar-expand-lg navbar-dark mb-4">
                        <div class="container">
                            <a class="navbar-brand" href="/">
                                <i class="fas fa-envelope-open-text me-2"></i>Sndr
                            </a>
                            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                                <span class="navbar-toggler-icon"></span>
                            </button>
                            <div class="collapse navbar-collapse" id="navbarNav">
                                <ul class="navbar-nav ms-auto">
                                    <li class="nav-item">
                                        <a class="nav-link" href="/"><i class="fas fa-home me-1"></i> Home</a>
                                    </li>
                                    {% if current_user.is_authenticated %}
                                    <li class="nav-item">
                                        <a class="nav-link" href="{{ url_for('inbox', username=current_user.username) }}">
                                            <i class="fas fa-inbox me-1"></i> Inbox
                                        </a>
                                    </li>
                                    <li class="nav-item">
                                        <a class="nav-link" href="{{ url_for('profile', username=current_user.username) }}">
                                            <i class="fas fa-user me-1"></i> Profile
                                        </a>
                                    </li>
                                    <li class="nav-item">
                                        <a class="nav-link" href="{{ url_for('logout') }}">
                                            <i class="fas fa-sign-out-alt me-1"></i> Logout
                                        </a>
                                    </li>
                                    {% else %}
                                    <li class="nav-item">
                                        <a class="nav-link" href="{{ url_for('login') }}">
                                            <i class="fas fa-sign-in-alt me-1"></i> Login
                                        </a>
                                    </li>
                                    <li class="nav-item">
                                        <a class="nav-link" href="{{ url_for('register') }}">
                                            <i class="fas fa-user-plus me-1"></i> Register
                                        </a>
                                    </li>
                                    {% endif %}
                                </ul>
                            </div>
                        </div>
                    </nav>
                    
                    <div class="container mt-4">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                        {% for category, message in messages %}
                        <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                        {% endfor %}
                        {% endif %}
                        {% endwith %}
                        
                        {% block content %}{% endblock %}
                    </div>
                    
                    <footer class="bg-light mt-5 py-3">
                        <div class="container text-center">
                            <p class="mb-0">&copy; 2025 Sndr. All rights reserved.</p>
                        </div>
                    </footer>
                    
                    <!-- Bootstrap Bundle with Popper -->
                    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
                    
                    {% block scripts %}{% endblock %}
                </body>
                </html>
                ''')
            
            # Create a basic index.html file
            with open(os.path.join(template_dir, 'index.html'), 'w') as f:
                f.write('''
                {% extends "base.html" %}

                {% block content %}
                <div class="container">
                    <div class="row justify-content-center">
                        <div class="col-md-10 text-center">
                            <div class="p-5 mb-4 bg-light rounded-3 shadow-sm">
                                <div class="container-fluid py-5">
                                    <h1 class="display-5 fw-bold text-primary">Welcome to Sndr</h1>
                                    <p class="fs-4">The anonymous messaging platform that helps you connect honestly.</p>
                                    <hr class="my-4">
                                    <p class="lead">Create an account, share your link, and receive anonymous messages.</p>
                                    <div class="d-grid gap-2 d-sm-flex justify-content-sm-center mt-4">
                                        <a href="{{ url_for('register') }}" class="btn btn-primary btn-lg px-4 gap-3">
                                            <i class="fas fa-user-plus me-2"></i>Get Started
                                        </a>
                                        <a href="{{ url_for('login') }}" class="btn btn-outline-secondary btn-lg px-4">
                                            <i class="fas fa-sign-in-alt me-2"></i>Log In
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="row mt-5">
                        <div class="col-md-4 mb-4">
                            <div class="card h-100 shadow-sm">
                                <div class="card-body text-center">
                                    <i class="fas fa-user-shield fa-3x text-primary mb-3"></i>
                                    <h5 class="card-title">Anonymous Feedback</h5>
                                    <p class="card-text">Receive honest messages without knowing who sent them.</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 mb-4">
                            <div class="card h-100 shadow-sm">
                                <div class="card-body text-center">
                                    <i class="fas fa-share-alt fa-3x text-primary mb-3"></i>
                                    <h5 class="card-title">Easy Sharing</h5>
                                    <p class="card-text">Share your unique link with friends on social media.</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 mb-4">
                            <div class="card h-100 shadow-sm">
                                <div class="card-body text-center">
                                    <i class="fas fa-mobile-alt fa-3x text-primary mb-3"></i>
                                    <h5 class="card-title">Mobile Friendly</h5>
                                    <p class="card-text">Use Sndr on any device, anywhere, anytime.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                {% endblock %}
                ''')
                
            # Create login.html
            with open(os.path.join(template_dir, 'login.html'), 'w') as f:
                f.write('''
                {% extends "base.html" %}

                {% block title %}Login - Sndr{% endblock %}

                {% block content %}
                <div class="container py-5">
                    <div class="row justify-content-center">
                        <div class="col-12 col-md-8 col-lg-6 col-xl-5">
                            <div class="card auth-card">
                                <div class="card-body p-4 p-md-5">
                                    <div class="auth-header text-center mb-4">
                                        <i class="fas fa-sign-in-alt fa-3x text-primary mb-3"></i>
                                        <h2 class="display-6 fw-bold">Welcome Back</h2>
                                        <p class="text-muted fs-5">Sign in to access your messages</p>
                                    </div>

                                    <form method="POST" action="{{ url_for('login') }}" class="auth-form">
                                        <div class="form-floating mb-4">
                                            <input type="text" class="form-control form-control-lg" id="username" name="username" 
                                                placeholder="Username" required {% if username %}value="{{ username }}"{% endif %}>
                                            <label for="username"><i class="fas fa-user me-2"></i>Username</label>
                                        </div>

                                        <div class="form-floating mb-4">
                                            <input type="password" class="form-control form-control-lg" id="password" name="password" 
                                                placeholder="Password" required>
                                            <label for="password"><i class="fas fa-lock me-2"></i>Password</label>
                                        </div>

                                        <div class="form-check mb-4">
                                            <input class="form-check-input" type="checkbox" id="remember" name="remember">
                                            <label class="form-check-label" for="remember">
                                                Remember me
                                            </label>
                                        </div>

                                        <button type="submit" class="btn btn-primary btn-lg w-100 mb-4 py-3">
                                            <i class="fas fa-sign-in-alt me-2"></i>Sign In
                                        </button>

                                        <div class="auth-links text-center">
                                            <p class="mb-2 fs-5">Don't have an account? 
                                                <a href="{{ url_for('register') }}" class="text-primary fw-bold">Register here</a>
                                            </p>
                                            <p class="mb-0 fs-6">
                                                <a href="{{ url_for('forgot_password') }}" class="text-secondary">
                                                    <i class="fas fa-key me-1"></i>Forgot password?
                                                </a>
                                            </p>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                {% endblock %}
                ''')
                
            # Create register.html
            with open(os.path.join(template_dir, 'register.html'), 'w') as f:
                f.write('''
                {% extends "base.html" %}

                {% block title %}Register - Sndr{% endblock %}

                {% block content %}
                <div class="container py-5">
                    <div class="row justify-content-center">
                        <div class="col-12 col-md-8 col-lg-6 col-xl-5">
                            <div class="card auth-card">
                                <div class="card-body p-4 p-md-5">
                                    <div class="auth-header text-center mb-4">
                                        <i class="fas fa-user-plus fa-3x text-primary mb-3"></i>
                                        <h2 class="display-6 fw-bold">Create Your Account</h2>
                                        <p class="text-muted fs-5">Join Sndr to start receiving anonymous messages</p>
                                    </div>

                                    <form method="POST" action="{{ url_for('register') }}" class="auth-form">
                                        <div class="form-floating mb-4">
                                            <input type="text" class="form-control form-control-lg" id="username" name="username" 
                                                placeholder="Username" required minlength="3" 
                                                pattern="[a-zA-Z0-9_]+" title="Username can only contain letters, numbers, and underscores">
                                            <label for="username"><i class="fas fa-user me-2"></i>Username</label>
                                            <div class="form-text">3+ characters, letters, numbers, and underscores only</div>
                                        </div>

                                        <div class="form-floating mb-4">
                                            <input type="email" class="form-control form-control-lg" id="email" name="email" 
                                                placeholder="Email" required>
                                            <label for="email"><i class="fas fa-envelope me-2"></i>Email</label>
                                        </div>

                                        <div class="form-floating mb-4">
                                            <input type="password" class="form-control form-control-lg" id="password" name="password" 
                                                placeholder="Password" required minlength="8"
                                                pattern="(?=.*\\d)(?=.*[a-z])(?=.*[A-Z]).{8,}" 
                                                title="Must contain at least one number and one uppercase and lowercase letter, and at least 8 or more characters">
                                            <label for="password"><i class="fas fa-lock me-2"></i>Password</label>
                                            <div class="form-text">8+ characters, include uppercase, lowercase, and numbers</div>
                                        </div>

                                        <div class="form-floating mb-4">
                                            <input type="password" class="form-control form-control-lg" id="confirm_password" name="confirm_password" 
                                                placeholder="Confirm Password" required>
                                            <label for="confirm_password"><i class="fas fa-lock me-2"></i>Confirm Password</label>
                                        </div>

                                        <button type="submit" class="btn btn-primary btn-lg w-100 mb-4 py-3">
                                            <i class="fas fa-user-plus me-2"></i>Create Account
                                        </button>

                                        <div class="auth-links text-center">
                                            <p class="mb-0 fs-5">Already have an account? 
                                                <a href="{{ url_for('login') }}" class="text-primary fw-bold">Log in here</a>
                                            </p>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                {% endblock %}
                ''')
                
        except Exception as e:
            print(f"Error creating template directory: {str(e)}")
            
    if not os.path.exists(static_dir):
        try:
            os.makedirs(static_dir, exist_ok=True)
            print(f"Created static directory: {static_dir}")
            
            # Create a simple favicon in the static directory
            with open(os.path.join(static_dir, 'favicon.ico'), 'wb') as f:
                # This is a very small binary representation of a favicon
                # Just a pink square as a placeholder
                f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x18\x00h\x03\x00\x00\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\xffk\xb5\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00')
                
        except Exception as e:
            print(f"Error creating static directory: {str(e)}")
else:
    # Use relative paths for local development
    template_dir = os.path.abspath('templates')
    static_dir = os.path.abspath('static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
DATABASE = os.environ.get('DATABASE_URL', 'sndr.db')
UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads/profile_images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Global VAPID keys for push notifications
VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY', 'qkTfR2mPNH7aGbcEFWupEkwJr8MXeE65yNBODG2r6Uc')
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY', 'BPGqX5Vf4teDWVXYBU_1kSztDWSzA1PzUx5vY6isS_dsDeTEwZHfB9G_RV9J_n7lrIXRQrIxiFMxtptHXe5A6yQ')
VAPID_CLAIMS = {
    "sub": "mailto:admin@sndr.com"
}

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, profile_image, created_at, last_login=None, is_active=True):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.profile_image = profile_image
        self.created_at = created_at
        self.last_login = last_login
        self._is_active = is_active

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value

@login_manager.user_loader
def load_user(user_id):
    user = query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)
    if user:
        # Set a default profile image if None or empty string
        profile_image = user['profile_image'] if user['profile_image'] else 'default.jpg'
        
        return User(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            password_hash=user['password_hash'],
            profile_image=profile_image,
            created_at=user['created_at'],
            last_login=user['last_login'],
            is_active=user['is_active']
        )
    return None

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db(query, args=()):
    db = get_db()
    db.execute(query, args)
    db.commit()
    return db.execute('SELECT last_insert_rowid()').fetchone()[0]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_image(file):
    if file and allowed_file(file.filename):
        # Generate a unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return unique_filename
    return None

def validate_username(username):
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if not re.match("^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, ""

def validate_password(password):
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    return True, ""

# Routes
@app.route('/')
def index():
    print(f"Current working directory: {os.getcwd()}")
    print(f"Template folder: {app.template_folder}")
    print(f"Templates exist: {os.path.exists(app.template_folder)}")
    
    # Try multiple approaches to find the index.html file
    index_path = os.path.join(app.template_folder, 'index.html')
    backup_index_path = os.path.join(app.template_folder, 'index_backup.html')
    alt_index_path = os.path.join(os.getcwd(), 'templates', 'index.html')
    
    print(f"Index.html path: {index_path}")
    print(f"Index.html exists: {os.path.exists(index_path)}")
    print(f"Backup index.html path: {backup_index_path}")
    print(f"Backup index.html exists: {os.path.exists(backup_index_path)}")
    
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error rendering index template: {str(e)}")
        try:
            # Try using the backup template
            return render_template('index_backup.html')
        except Exception as e2:
            print(f"Error rendering backup template: {str(e2)}")
            # Fallback to hardcoded HTML if template can't be found
            return f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Sndr - Anonymous Messaging</title>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 0;
                        background-color: #f9f2f4;
                        color: #333;
                    }}
                    .container {{
                        width: 80%;
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        text-align: center;
                        padding: 40px 0;
                        background-color: #ff69b4;
                        color: white;
                        margin-bottom: 30px;
                    }}
                    .btn {{
                        display: inline-block;
                        background-color: #ff69b4;
                        color: white;
                        padding: 10px 20px;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 10px 0;
                        font-weight: bold;
                    }}
                    .feature-box {{
                        background-color: white;
                        border-radius: 8px;
                        padding: 20px;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .nav {{
                        text-align: center;
                    }}
                    .nav a {{
                        margin: 0 10px;
                        color: white;
                        text-decoration: none;
                        font-weight: bold;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Welcome to Sndr</h1>
                    <p>The anonymous messaging platform</p>
                    <div class="nav">
                        <a href="/login_direct">Log In</a> | 
                        <a href="/register_direct">Register</a> | 
                        <a href="/debug_info">Debug Info</a>
                    </div>
                    <a href="/login_direct" class="btn">Log In</a>
                    <a href="/register_direct" class="btn">Register</a>
                </div>
                
                <div class="container">
                    <div class="feature-box">
                        <h2>How it works</h2>
                        <p>Register for an account, share your unique link, and receive anonymous messages from friends, colleagues, or admirers.</p>
                    </div>
                    
                    <div class="feature-box">
                        <h2>Features</h2>
                        <ul>
                            <li>Anonymous messaging</li>
                            <li>Personalized messaging page</li>
                            <li>Interactive message inbox</li>
                            <li>Beautiful pink-themed design</li>
                        </ul>
                    </div>
                    
                    <div class="feature-box">
                        <p>Note: Using fallback HTML mode since templates couldn't be loaded.</p>
                        <p>For full functionality, please use the direct navigation links above.</p>
                    </div>
                </div>
            </body>
            </html>
            """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print(f"[DEBUG] User already logged in: {current_user.username}")
        return redirect(url_for('inbox', username=current_user.username))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        print(f"[DEBUG] Login attempt for username: {username}")
        
        # Check if username exists
        user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        if not user:
            print(f"[DEBUG] Username not found: {username}")
            flash('Username not found. Please check your username or register for an account.', 'error')
            try:
                return render_template('login.html', username=username)
            except Exception:
                # Fallback to direct HTML version
                return login_direct()
        
        # Check password
        if not check_password_hash(user['password_hash'], password):
            print(f"[DEBUG] Invalid password for username: {username}")
            flash('Invalid password. Please try again or reset your password.', 'error')
            try:
                return render_template('login.html', username=username)
            except Exception:
                # Fallback to direct HTML version
                return login_direct()
        
        if not user['is_active']:
            print(f"[DEBUG] Inactive account attempt: {username}")
            flash('This account is no longer active', 'error')
            return redirect(url_for('login'))
            
        user_obj = User(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            password_hash=user['password_hash'],
            profile_image=user['profile_image'] if user['profile_image'] else 'default.jpg',
            created_at=user['created_at'],
            last_login=user['last_login'],
            is_active=user['is_active']
        )
        login_user(user_obj, remember=remember)
        print(f"[DEBUG] User logged in successfully: {username}")
        
        # Update last login
        db = get_db()
        db.execute('UPDATE users SET last_login = ? WHERE id = ?',
                  [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user['id']])
        db.commit()
        
        print(f"[DEBUG] Redirecting to inbox for user: {user_obj.username}")
        return redirect(url_for('inbox', username=user_obj.username))
    
    try:
        return render_template('login.html')
    except Exception as e:
        print(f"[DEBUG] Template error in login: {str(e)}")
        # Fallback to direct HTML version
        return login_direct()

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate username
        is_valid, message = validate_username(username)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('register'))
        
        # Validate email
        try:
            validate_email(email)
        except EmailNotValidError as e:
            flash(str(e), 'error')
            return redirect(url_for('register'))
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
        
        # Check if username or email already exists
        existing_user = query_db('SELECT * FROM users WHERE username = ? OR email = ?',
                               [username, email], one=True)
        if existing_user:
            if existing_user['username'] == username:
                flash('Username already exists', 'error')
            else:
                flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        password_hash = generate_password_hash(password)
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        user_id = insert_db('''
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        ''', [username, email, password_hash, created_at])
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    try:
        return render_template('register.html')
    except Exception as e:
        print(f"[DEBUG] Template error in register: {str(e)}")
        # Fallback to direct HTML version
        return register_direct()

@app.route('/u/<username>')
def profile(username):
    user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    if user is None:
        flash('User not found', 'error')
        return redirect(url_for('index'))
    
    # Set a default profile image if None or empty string
    if not user['profile_image']:
        user = dict(user)  # Convert to dict to make it mutable
        user['profile_image'] = 'default.jpg'
        
    return render_template('profile.html', user=user)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    try:
        # Handle profile image upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file.filename != '':
                filename = save_profile_image(file)
                if filename:
                    db = get_db()
                    db.execute('UPDATE users SET profile_image = ? WHERE id = ?', 
                              [filename, current_user.id])
                    db.commit()
                    flash('Profile image updated!', 'success')
                else:
                    flash('Invalid file type. Please upload a valid image (JPG, PNG, GIF).', 'error')
            
        return redirect(url_for('profile', username=current_user.username))
    except Exception as e:
        print(f"Error updating profile: {e}")
        flash('Error updating profile. Please try again.', 'error')
        return redirect(url_for('profile', username=current_user.username))

@app.route('/reply_to_instagram/<message_id>', methods=['GET'])
@login_required
def reply_to_instagram(message_id):
    try:
        # Get the message content
        message = query_db('SELECT * FROM messages WHERE id = ? AND user_id = ?',
                         [message_id, current_user.id], one=True)
        if not message:
            flash('Message not found', 'error')
            return redirect(url_for('inbox', username=current_user.username))
        
        # Prepare message text for Instagram - truncate if too long
        message_text = message['content']
        if len(message_text) > 100:
            message_text = message_text[:97] + '...'
        
        # Create Instagram story deep link
        # Note: This uses a URL scheme that will open Instagram stories
        # Instagram URL scheme: instagram://story-camera
        
        instagram_url = 'instagram://story-camera'
        
        # Mark message as read if not already
        if not message['read']:
            db = get_db()
            db.execute('UPDATE messages SET read = 1 WHERE id = ?', [message_id])
            db.commit()
        
        # Note: We can't directly share text to Instagram stories via URL
        # The user will need to manually paste the message text
        flash('Instagram will open. Copy and paste your message there to share it!', 'info')
        
        # We'll return a page that auto-redirects to Instagram and displays the message to copy
        return render_template('redirect_to_instagram.html', 
                              message=message_text,
                              instagram_url=instagram_url)
    
    except Exception as e:
        print(f"Error replying to Instagram: {e}")
        flash('Error opening Instagram. Please try manually.', 'error')
        return redirect(url_for('inbox', username=current_user.username))

@app.route('/send', methods=['POST'])
def send_message():
    try:
        username = request.form.get('username')
        message = request.form.get('message')
        
        if not username or not message:
            flash('Username and message are required', 'error')
            return redirect(url_for('profile', username=username))
        
        if len(message.strip()) == 0:
            flash('Message cannot be empty', 'error')
            return redirect(url_for('profile', username=username))
        
        user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('index'))
        
        if not user['is_active']:
            flash('This user account is no longer active', 'error')
            return redirect(url_for('index'))
        
        # Insert message into database
        message_id = insert_db('''
            INSERT INTO messages (content, user_id, created_at)
            VALUES (?, ?, ?)
        ''', [message.strip(), user['id'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        
        # Send push notification
        notification_title = "New Anonymous Message"
        notification_body = "Someone sent you an anonymous message! Tap to view."
        notification_url = url_for('inbox', username=username, _external=True)
        
        send_push_notification(
            user_id=user['id'],
            title=notification_title,
            body=notification_body,
            url=notification_url
        )
        
        flash('Message sent successfully!', 'success')
    except Exception as e:
        print(f"Error sending message: {e}")
        flash('Error sending message. Please try again.', 'error')
    
    return redirect(url_for('profile', username=username))

@app.route('/inbox/<username>')
@login_required
def inbox(username):
    try:
        print(f"[DEBUG] Accessing inbox for username in URL: {username}")
        print(f"[DEBUG] Current logged-in user: {current_user.username}")
        
        # First check if the user exists
        user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        print(f"[DEBUG] User from DB: {user}")
        if not user:
            print(f"[DEBUG] User not found: {username}")
            flash('User not found', 'error')
            return redirect(url_for('index'))
        print(f"[DEBUG] User is_active: {user['is_active']}")
        
        # Then check if the current user is authorized to view this inbox
        if current_user.username != username:
            print(f"[DEBUG] Unauthorized access attempt: {current_user.username} trying to access {username}'s inbox")
            flash('You can only view your own inbox', 'error')
            return redirect(url_for('index'))
        
        # Get messages with proper error handling
        try:
            print(f"[DEBUG] Fetching messages for user_id: {current_user.id}")
            messages = query_db('''
                SELECT id, content, created_at, 
                       CASE WHEN read = 1 THEN 1 ELSE 0 END as is_read
                FROM messages 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', [current_user.id])
            
            if messages is None:
                print("[DEBUG] No messages found")
                messages = []
            else:
                print(f"[DEBUG] Found {len(messages)} messages")
                
        except sqlite3.Error as e:
            print(f"[DEBUG] Database error in inbox: {str(e)}")
            flash('Error loading messages. Please try again.', 'error')
            return redirect(url_for('index'))
        
        print("[DEBUG] Successfully loaded inbox")
        return render_template('inbox.html', messages=messages, user=user)
        
    except Exception as e:
        print(f"[DEBUG] Unexpected error in inbox route: {str(e)}")
        import traceback
        print(traceback.format_exc())
        flash('Error loading inbox. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/uploads/profile_images/<filename>')
def uploaded_file(filename):
    # Ensure the file exists or return a default image
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], 'default.jpg')
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/mark_as_read/<int:message_id>', methods=['POST'])
@login_required
def mark_as_read(message_id):
    try:
        message = query_db('SELECT * FROM messages WHERE id = ? AND user_id = ?',
                         [message_id, current_user.id], one=True)
        if not message:
            return jsonify({'success': False, 'error': 'Message not found'}), 404
        
        db = get_db()
        db.execute('UPDATE messages SET read = 1 WHERE id = ?', [message_id])
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error marking message as read: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/delete_message/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    try:
        # Verify the message belongs to the current user
        message = query_db('SELECT * FROM messages WHERE id = ? AND user_id = ?',
                         [message_id, current_user.id], one=True)
        if not message:
            return jsonify({'success': False, 'error': 'Message not found'}), 404
        
        db = get_db()
        db.execute('DELETE FROM messages WHERE id = ?', [message_id])
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error deleting message: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/profile')
@login_required
def my_profile():
    return redirect(url_for('profile', username=current_user.username))

# Password reset functionality
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Validate email format
        try:
            validate_email(email)
        except EmailNotValidError:
            flash('Please enter a valid email address', 'error')
            return render_template('forgot_password.html')
        
        # Check if email exists
        user = query_db('SELECT * FROM users WHERE email = ?', [email], one=True)
        if not user:
            # Don't reveal if email exists or not (security best practice)
            flash('If this email is registered, you will receive a password reset link shortly.', 'info')
            return redirect(url_for('login'))
        
        # Generate token
        token = secrets.token_urlsafe(32)
        token_expiry = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Store token in database
        try:
            # First, expire any existing tokens
            db = get_db()
            db.execute('DELETE FROM password_reset_tokens WHERE user_id = ?', [user['id']])
            
            # Then insert new token
            db.execute('''
                INSERT INTO password_reset_tokens (user_id, token, expiry_date)
                VALUES (?, ?, ?)
            ''', [user['id'], token, token_expiry])
            db.commit()
            
            # Generate reset link
            reset_link = url_for('reset_password', token=token, _external=True)
            
            # In a real app, you would send an email here
            # For demo, we'll just flash the link
            print(f"[DEBUG] Reset link for {email}: {reset_link}")
            flash(f'Reset link (for demo purposes): <a href="{reset_link}">Reset Password</a>', 'info')
            
            flash('If this email is registered, you will receive a password reset link shortly.', 'info')
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"[DEBUG] Error generating reset token: {e}")
            flash('An error occurred. Please try again later.', 'error')
    
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Check if token exists and is valid
    token_data = query_db('''
        SELECT user_id, expiry_date FROM password_reset_tokens 
        WHERE token = ? AND expiry_date > ?
    ''', [token, datetime.now().strftime('%Y-%m-%d %H:%M:%S')], one=True)
    
    if not token_data:
        flash('Invalid or expired password reset link', 'error')
        return redirect(url_for('forgot_password'))
    
    user = query_db('SELECT * FROM users WHERE id = ?', [token_data['user_id']], one=True)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message, 'error')
            return render_template('reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', token=token)
        
        # Update password
        try:
            db = get_db()
            db.execute('UPDATE users SET password_hash = ? WHERE id = ?', 
                       [generate_password_hash(password), user['id']])
            
            # Delete used token
            db.execute('DELETE FROM password_reset_tokens WHERE token = ?', [token])
            db.commit()
            
            flash('Your password has been reset! You can now log in with your new password.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"[DEBUG] Error resetting password: {e}")
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('reset_password.html', token=token)

@app.route('/debug_info')
def debug_info():
    import os
    
    # Get root directory contents
    root_contents = []
    try:
        if os.path.exists('/opt/render/project/src'):
            root_contents = os.listdir('/opt/render/project/src')
    except Exception as e:
        root_contents = str(e)
        
    # Attempt to find templates
    possible_template_paths = [
        '/opt/render/project/src/templates',
        os.path.join(os.getcwd(), 'templates'),
        os.path.abspath('templates'),
        app.template_folder
    ]
    
    template_path_checks = {}
    for path in possible_template_paths:
        try:
            template_path_checks[path] = {
                'exists': os.path.exists(path),
                'contents': os.listdir(path) if os.path.exists(path) else 'N/A',
                'isdir': os.path.isdir(path) if os.path.exists(path) else 'N/A'
            }
        except Exception as e:
            template_path_checks[path] = str(e)
    
    info = {
        'cwd': os.getcwd(),
        'template_folder': app.template_folder,
        'static_folder': app.static_folder,
        'template_folder_exists': os.path.exists(app.template_folder),
        'template_path_checks': template_path_checks,
        'root_dir_contents': root_contents,
        'render_root_exists': os.path.exists('/opt/render'),
        'env_vars': {k: v for k, v in os.environ.items() if not k.startswith('_')}
    }
    return jsonify(info)

@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(e):
    return f"""
    <html>
    <head><title>Template Error</title></head>
    <body>
        <h1>Template Error</h1>
        <p>The template file could not be found: {e}</p>
        <p>Current working directory: {os.getcwd()}</p>
        <p>Template folder path: {app.template_folder}</p>
        <p>Template folder exists: {os.path.exists(app.template_folder)}</p>
        <p>Try visiting the <a href="/debug_info">debug info page</a> for more information.</p>
    </body>
    </html>
    """, 500

@app.route('/register_direct')
def register_direct():
    """Direct HTML registration page when templates don't load."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Register - Sndr</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 0;
                background-color: #f9f2f4;
                color: #333;
            }}
            .container {{
                width: 80%;
                max-width: 500px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                text-align: center;
                padding: 20px 0;
                background-color: #ff69b4;
                color: white;
                margin-bottom: 30px;
            }}
            .form-group {{
                margin-bottom: 15px;
            }}
            label {{
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }}
            input[type="text"],
            input[type="email"],
            input[type="password"] {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            .btn {{
                display: inline-block;
                background-color: #ff69b4;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
            }}
            .form-box {{
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .messages {{
                margin-bottom: 15px;
            }}
            .message {{
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 4px;
            }}
            .error {{
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
            }}
            .success {{
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Register for Sndr</h1>
        </div>
        
        <div class="container">
            <div class="form-box">
                <form method="POST" action="/register">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="confirm_password">Confirm Password</label>
                        <input type="password" id="confirm_password" name="confirm_password" required>
                    </div>
                    
                    <button type="submit" class="btn">Register</button>
                </form>
                
                <p>Already have an account? <a href="/login">Log in</a></p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/login_direct')
def login_direct():
    """Direct HTML login page when templates don't load."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - Sndr</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 0;
                background-color: #f9f2f4;
                color: #333;
            }}
            .container {{
                width: 80%;
                max-width: 500px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                text-align: center;
                padding: 20px 0;
                background-color: #ff69b4;
                color: white;
                margin-bottom: 30px;
            }}
            .form-group {{
                margin-bottom: 15px;
            }}
            label {{
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }}
            input[type="text"],
            input[type="password"] {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            .btn {{
                display: inline-block;
                background-color: #ff69b4;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
            }}
            .form-box {{
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .remember-me {{
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Login to Sndr</h1>
        </div>
        
        <div class="container">
            <div class="form-box">
                <form method="POST" action="/login">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    
                    <div class="remember-me">
                        <input type="checkbox" id="remember" name="remember">
                        <label for="remember" style="display: inline;">Remember me</label>
                    </div>
                    
                    <button type="submit" class="btn">Login</button>
                </form>
                
                <p>Don't have an account? <a href="/register">Register</a></p>
                <p><a href="/forgot_password">Forgot password?</a></p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')

# Push notification subscription endpoint
@app.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    try:
        subscription_data = request.json.get('subscription')
        
        if not subscription_data:
            return jsonify({"error": "Subscription data is missing"}), 400
            
        endpoint = subscription_data.get('endpoint')
        p256dh = subscription_data.get('keys', {}).get('p256dh')
        auth = subscription_data.get('keys', {}).get('auth')
        
        if not endpoint or not p256dh or not auth:
            return jsonify({"error": "Subscription data is incomplete"}), 400
            
        # Check if subscription already exists for this user
        existing_sub = query_db('''
            SELECT * FROM push_subscriptions 
            WHERE user_id = ? AND endpoint = ?
        ''', [current_user.id, endpoint], one=True)
        
        if existing_sub:
            # Subscription already exists
            return jsonify({"success": True, "message": "Subscription already exists"}), 200
            
        # Insert new subscription
        insert_db('''
            INSERT INTO push_subscriptions (user_id, endpoint, p256dh, auth, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            current_user.id, 
            endpoint, 
            p256dh, 
            auth, 
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ])
        
        print(f"[DEBUG] Saved push subscription for user {current_user.username}")
        return jsonify({"success": True, "message": "Subscription saved"}), 201
        
    except Exception as e:
        print(f"[DEBUG] Error saving subscription: {str(e)}")
        return jsonify({"error": f"Failed to save subscription: {str(e)}"}), 500

def send_push_notification(user_id, title, body, url=None):
    """Send push notification to all subscriptions for a user"""
    try:
        # Get all subscriptions for the user
        subscriptions = query_db('''
            SELECT * FROM push_subscriptions WHERE user_id = ?
        ''', [user_id])
        
        if not subscriptions:
            print(f"[DEBUG] No push subscriptions found for user_id {user_id}")
            return
            
        payload = {
            "title": title,
            "body": body,
            "url": url if url else ""
        }
        
        expired_endpoints = []
        
        for sub in subscriptions:
            subscription_info = {
                "endpoint": sub['endpoint'],
                "keys": {
                    "p256dh": sub['p256dh'],
                    "auth": sub['auth']
                }
            }
            
            try:
                webpush(
                    subscription_info=subscription_info,
                    data=json.dumps(payload),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims=VAPID_CLAIMS
                )
                print(f"[DEBUG] Push notification sent to {sub['endpoint']}")
            except WebPushException as e:
                print(f"[DEBUG] Push error: {e}")
                if e.response and e.response.status_code == 410:
                    # Subscription expired
                    expired_endpoints.append(sub['endpoint'])
                    
        # Remove expired subscriptions
        if expired_endpoints:
            db = get_db()
            for endpoint in expired_endpoints:
                db.execute('DELETE FROM push_subscriptions WHERE endpoint = ?', [endpoint])
            db.commit()
            print(f"[DEBUG] Removed {len(expired_endpoints)} expired push subscriptions")
    
    except Exception as e:
        print(f"[DEBUG] Error sending push notifications: {str(e)}")

# Add an endpoint to serve the service worker from root path
@app.route('/service-worker.js')
def service_worker():
    response = send_from_directory(os.path.join(app.static_folder, 'js'), 'service-worker.js')
    # Add Service-Worker-allowed header to resolve scope issues
    response.headers['Service-Worker-Allowed'] = '/'
    # Cache for a short time
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/get-vapid-public-key')
def get_vapid_public_key():
    return jsonify({"publicKey": VAPID_PUBLIC_KEY})

# Add an endpoint for checking new messages (polling)
@app.route('/check_messages')
@login_required
def check_messages():
    try:
        # Get the timestamp from the request
        since_timestamp = request.args.get('since', '0')
        
        # Convert to float (epoch time)
        try:
            since_time = float(since_timestamp)
        except ValueError:
            since_time = 0
            
        # Convert epoch to datetime for database query
        since_datetime = datetime.fromtimestamp(since_time).strftime('%Y-%m-%d %H:%M:%S')
        
        # Get count of new messages
        new_messages = query_db('''
            SELECT COUNT(*) as count 
            FROM messages 
            WHERE user_id = ? AND created_at > ? AND read = 0
        ''', [current_user.id, since_datetime], one=True)
        
        # Get current time as epoch timestamp
        current_time = datetime.now().timestamp()
        
        return jsonify({
            'success': True,
            'new_messages': new_messages['count'] if new_messages else 0,
            'current_time': current_time
        })
        
    except Exception as e:
        print(f"[DEBUG] Error checking messages: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to check messages'
        })

# Add routes for PWA
@app.route('/manifest.json')
def manifest():
    return send_from_directory(app.static_folder, 'manifest.json')

@app.route('/pwa-service-worker.js')
def pwa_service_worker():
    response = send_from_directory(os.path.join(app.static_folder, 'js'), 'pwa-service-worker.js')
    # Set headers for service worker
    response.headers['Service-Worker-Allowed'] = '/'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Content-Type'] = 'application/javascript'
    return response

# Add offline fallback page
@app.route('/offline')
def offline():
    return render_template('offline.html')

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    
    # Only use ngrok in development, not on Render
    if not is_render:
        try:
            run_with_ngrok(app)
        except NameError:
            # If run_with_ngrok is not defined, continue without it
            pass
    
    # Use the PORT environment variable if available (for Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
