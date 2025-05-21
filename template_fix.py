"""
This file contains the code changes needed to fix the template not found error on Render.com.
Replace the beginning of your app.py file with this code.
"""

# Import statements remain the same
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

# Configuration
# Check if we're running on Render
if os.path.exists('/opt/render'):
    # Use Render.com specific paths
    template_dir = '/opt/render/project/src/templates'
    static_dir = '/opt/render/project/src/static'
else:
    # Use relative paths for local development
    template_dir = os.path.abspath('templates')
    static_dir = os.path.abspath('static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
DATABASE = os.environ.get('DATABASE_URL', 'sndr.db')

# Replace your index route with this:
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error rendering template: {str(e)}")
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
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Welcome to Sndr</h1>
                <p>The anonymous messaging platform</p>
                <a href="/login" class="btn">Log In</a>
                <a href="/register" class="btn">Register</a>
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
                    <p>This is a fallback page. Visit <a href="/debug_info">Debug Info</a> for more details.</p>
                </div>
            </div>
        </body>
        </html>
        """

# Add this debug info route at the end of the file
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