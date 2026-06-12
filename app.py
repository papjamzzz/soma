from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
# Re-read templates from disk on every request (dev convenience)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({'status': 'ok', 'project': 'soma'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5573, debug=False)
