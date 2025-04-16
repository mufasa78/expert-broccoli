import os
from flask import Flask, render_template, session, redirect, url_for, request, flash

# Create the Flask application instance
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

# Setup a secret key, required by sessions
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"

# Import text utilities
from i18n.translations import get_text

@app.route('/')
def index():
    # Set default language to Chinese if not set
    if 'lang' not in session:
        session['lang'] = 'zh'

    return render_template('index.html',
                          title=get_text('app_title', session.get('lang', 'zh')),
                          lang=session.get('lang', 'zh'))

@app.route('/switch_language/<lang>')
def switch_language(lang):
    if lang in ['zh', 'en']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
