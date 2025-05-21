# Render.com Deployment Fix

The deployment is failing because Flask can't find the template files. Here are the changes needed to fix the issue:

## 1. Update app.py to explicitly set template and static folders

Add these lines after the imports and before the Flask app initialization:

```python
# Configuration
template_dir = os.path.abspath('templates')
static_dir = os.path.abspath('static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
```

Replace the current `app = Flask(__name__)` line with the code above.

## 2. Add debug info route

Add this route at the end of your file to help diagnose issues:

```python
import jinja2

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

@app.route('/debug_info')
def debug_info():
    import os
    info = {
        'cwd': os.getcwd(),
        'template_folder': app.template_folder,
        'static_folder': app.static_folder,
        'template_folder_exists': os.path.exists(app.template_folder),
        'templates_dir_contents': os.listdir(app.template_folder) if os.path.exists(app.template_folder) else 'N/A',
        'static_folder_exists': os.path.exists(app.static_folder),
        'static_dir_contents': os.listdir(app.static_folder) if os.path.exists(app.static_folder) else 'N/A',
        'env_vars': {k: v for k, v in os.environ.items() if not k.startswith('_')}
    }
    return jsonify(info)
```

## 3. Render.com Specific Configuration

In the Render.com dashboard:

1. Go to the Environment section
2. Add a new environment variable:
   - Key: `PYTHONPATH`
   - Value: `/opt/render/project/src`

This will help Python find the modules and templates correctly.

## 4. Alternative Fix: Use Absolute Paths

If the above doesn't work, try updating the Flask app initialization to use absolute paths with the Render.com's specific directory structure:

```python
app = Flask(__name__, 
            template_folder='/opt/render/project/src/templates',
            static_folder='/opt/render/project/src/static')
```

Make this change and redeploy the application.

## 5. Project Structure Check

Ensure your project structure on GitHub has these directories at the top level:
- templates/ (with index.html and other template files)
- static/ (with CSS, JS, etc.)
- app.py (main application file)
- requirements.txt 