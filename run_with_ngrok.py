import os
from flask_ngrok import run_with_ngrok
from app import app

print("Starting Sndr app with ngrok tunnel...")
print("This will make your app available on the internet so you can install it on your phone")
print("-----------------------------------------------------------------------------------")

# Get the database path from app
DATABASE = os.environ.get('DATABASE_URL', 'sndr.db')

# Initialize DB if needed
if not os.path.exists(DATABASE):
    from app import init_db
    with app.app_context():
        init_db()
        print("Database initialized")

# Add ngrok
run_with_ngrok(app)

# Print instructions
print("\nAfter starting, look for the ngrok URL (https://something.ngrok.io)")
print("Open this URL on your phone to install the PWA\n")
print("-----------------------------------------------------------------------------------")

# Run the app
app.run() 