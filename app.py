from flask import Flask, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/token_metadata.json')
def serve_json():
    return send_file('token_metadata.json', mimetype='application/json')

@app.route('/')
def index():
    return "Token Metadata Service is running"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)