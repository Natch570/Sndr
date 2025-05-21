# Sndr - Anonymous Messaging Web App

Sndr is a web application that allows users to receive anonymous messages from others. Perfect for secret admirers, collecting feedback, or just having fun!

## Features

- User registration with unique usernames
- Personalized pages for receiving messages (e.g., sndr.com/u/username)
- Anonymous message submission
- Inbox to view all received messages
- Clean, responsive UI with a pink theme and envelope animations

## Setup Instructions

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd sndr
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the Flask development server:
   ```
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Deployment on Render.com

1. Create a new account or log in to [Render.com](https://render.com)
2. From the dashboard, click on "New +" and select "Web Service"
3. Connect your GitHub repository or paste the GitHub URL
4. Configure the deployment:
   - Name: Sndr (or your preferred name)
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Select your desired instance type (Free tier works for testing)
6. Click "Create Web Service"

### Environment Variables
You may need to set the following environment variables in the Render dashboard:
- `SECRET_KEY`: A secure random string for session security
- `DATABASE_URL`: If using a different database than SQLite

## Optional Enhancements

Future enhancements could include:
- CAPTCHA to prevent spam
- Message reactions/likes
- Moderation features
- Profanity filters

## License

This project is licensed under the MIT License - see the LICENSE file for details.
