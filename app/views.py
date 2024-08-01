from app import app, db

from flask_cors import CORS

from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='react/build', template_folder='react/build')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/some_endpoint', methods=['GET'])
def some_endpoint():
    pass

if __name__ == "__main__":
    app.run(debug=True)
