# Sndr Deployment Guide

To make Sndr accessible from your phone and install it as a PWA, you need to deploy it to a public HTTPS URL.

## Easy Deployment with Render.com (Recommended)

1. **Create a Render account**
   - Sign up at [render.com](https://render.com)
   - It's free and doesn't require a credit card

2. **Create a new Web Service**
   - Click "New +" and select "Web Service"
   - Connect to your GitHub or upload this code

3. **Configure the service**
   - Name: `sndr` (or any name you like)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (takes about 5-10 minutes the first time)
   - Render will provide a public HTTPS URL (like `https://sndr.onrender.com`)

5. **Access on your phone**
   - Open the URL on your phone
   - Log in to Sndr
   - Tap "Install App" in the navigation bar or use the floating button

## Alternative: PythonAnywhere (Also Easy)

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com) (free tier available)
2. Upload your code or clone from GitHub
3. Set up a new web app with Flask
4. Configure your WSGI file to use your app.py
5. Access at yourusername.pythonanywhere.com

## Alternative: Heroku (Requires credit card for verification)

1. Sign up at [heroku.com](https://www.heroku.com)
2. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Run the following commands:
   ```
   heroku login
   heroku create sndr-app
   git push heroku main
   ```
4. Access at the provided domain (like `https://sndr-app.herokuapp.com`)

## Need help?

- Make sure your `requirements.txt`, `Procfile`, and `runtime.txt` are included
- Check the hosting provider's logs if you encounter any issues
- Consider using a free GitHub account to store your code for easy deployment

Your app needs to be on a public HTTPS URL for the PWA features to work properly on your phone. 