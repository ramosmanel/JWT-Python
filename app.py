from flask import Flask, request, jsonify, make_response, render_template, session
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
print(os.getenv('SECRET_KEY'))

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return func(*args, **kwargs)
    return decorated

#Home
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return 'Logged in currently!'

#Publi
@app.route('/public')
def public():
    return 'For Public'

#Authenticated
@app.route('/auth')
@token_required
def auth():
    return 'JWT is verified. Welcome to your dashboard!'

#Login
@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] and request.form['password'] == 'MyPassword123':
        session['logged_in'] = True

        token = jwt.encode({
            'user': request.form['username'],
            'expiration': (datetime.now(timezone.utc) + timedelta(seconds=120)).isoformat()
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
    else:
        return make_response('Unable to verify', 403,
                             {'WWW-Authenticate': 'Basic realm: "Authentication failed!"'})

if __name__  == "__main__":
    app.run(debug=True)