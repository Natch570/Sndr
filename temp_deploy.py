"""
Temporary Deployment Guide for Sndr

This script provides instructions for deploying Sndr so it can be
accessed from a mobile device for PWA installation.
"""

import os
import webbrowser

print("\n===================================================")
print("SNDR DEPLOYMENT FOR MOBILE INSTALLATION")
print("===================================================\n")

print("To install Sndr as a PWA on your phone, you need to:")
print("1. Host the application on a public HTTPS URL")
print("2. Access that URL from your phone")
print("3. Use the 'Install App' button in the app\n")

print("FREE HOSTING OPTIONS:")
print("---------------------")
print("1. RENDER.COM (Recommended, free tier available)")
print("   - Create an account at render.com")
print("   - Create a new Web Service")
print("   - Connect to your GitHub repository or upload the code")
print("   - Choose Python as the runtime environment")
print("   - Set build command: 'pip install -r requirements.txt'")
print("   - Set start command: 'python app.py'")
print("   - Deploy and use the provided HTTPS URL on your phone\n")

print("2. PYTHONANYWHERE (Simple, free tier available)")
print("   - Create an account at pythonanywhere.com")
print("   - Upload your code using their file browser")
print("   - Set up a web app with Flask")
print("   - Configure WSGI file to point to your app")
print("   - Use the provided domain (yourusername.pythonanywhere.com)\n")

print("3. HEROKU (Popular, credit card required for free tier)")
print("   - Create an account at heroku.com")
print("   - Install Heroku CLI")
print("   - Run: heroku create")
print("   - Run: git push heroku main")
print("   - Access at the provided domain\n")

print("LOCAL TESTING WITH TUNNELING (NOT RECOMMENDED FOR PWA):")
print("-----------------------------------------------------")
print("For temporary testing, you can use tunneling services like:")
print("- ngrok: https://ngrok.com/ (limited free tunnels)")
print("- cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/")
print("- localtunnel: https://localtunnel.github.io/www/")
print("\nNote: These solutions might not work well for PWAs due to:")
print("- HTTPS certificate issues")
print("- Temporary URL changes between sessions")
print("- Service worker scope limitations\n")

print("===================================================")
print("Would you like to open any of these services in your browser?")
print("1. Render.com")
print("2. PythonAnywhere")
print("3. Heroku")
print("4. None/Exit")

try:
    choice = input("Enter your choice (1-4): ")
    if choice == "1":
        webbrowser.open("https://render.com")
    elif choice == "2":
        webbrowser.open("https://www.pythonanywhere.com")
    elif choice == "3":
        webbrowser.open("https://www.heroku.com")
    print("\nGood luck with your deployment!")
except Exception as e:
    print(f"Error: {e}")
    print("You can manually visit these websites to deploy your app.") 