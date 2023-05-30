from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.models import User
from datetime import datetime

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify(username, password):
    user= User.query.filter_by(username=username).first()
    if user is not None and user.check_password(password):
        return user
    
@token_auth.verify_token
def verify_token(token):
    now = datetime.utcnow()
    check_token = User.query.filter_by(token=token).first()
    if check_token is None and check_token.token_expiration > now:
        return check_token