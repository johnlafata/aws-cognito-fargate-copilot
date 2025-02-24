from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import os

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Use a secure random key in production
oauth = OAuth(app)

COGNITO_USER_POOL_ID = os.getenv('USER_POOL_ID')
logger.info(f'COGNITO_USER_POOL_ID: {COGNITO_USER_POOL_ID}')
COGNITO_CLIENT_ID = os.getenv('USER_POOL_CLIENT_ID')
logger.info(f'COGNITO_CLIENT_ID: {COGNITO_CLIENT_ID}')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
logger.info(f'AWS_REGION: {AWS_REGION}')
SERVICE_NAME = os.getenv('COPILOT_SERVICE_NAME')
logger.info(f'SERVICE_NAME: {SERVICE_NAME}')
APP = os.getenv('COPILOT_APPLICATION_NAME')
logger.info(f'APP: {APP}')
ENV = os.getenv('COPILOT_ENVIRONMENT_NAME')
logger.info(f'ENV: {ENV}')
DOMAIN = os.getenv('DOMAIN_NAME')
logger.info(f'DOMAIN: {DOMAIN}')


if SERVICE_NAME is  None or ENV is None or APP is None or DOMAIN is None:
    BASE_URL = 'http://localhost:8080'
else:
    BASE_URL = 'https://' + SERVICE_NAME + '.' + ENV+ "."+ APP+ "."+ DOMAIN
logger.info(f'BASE_URL: {BASE_URL}')

REDIRECT_URI = BASE_URL+'/authorize'
logger.info(f'REDIRECT_URI: {REDIRECT_URI}')
LOGOUT_URI = BASE_URL + '/logout'
logger.info(f'LOGOUT_URI: {LOGOUT_URI}')

oidc_session_initialized=False
if COGNITO_USER_POOL_ID is None or COGNITO_CLIENT_ID is None:
    logger.info('COGNITO_USER_POOL_ID and COGNITO_CLIENT_ID must be set for authentication')
else:
    logger.info('COGNITO_USER_POOL_ID and COGNITO_CLIENT_ID are set')
    authorizationUrl=f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
    logger.info(f'authorizationUrl: {authorizationUrl}')
    server_metadata_url= authorizationUrl+'/.well-known/openid-configuration'
    logger.info(f'server_metadata_url: {server_metadata_url}')
    oauth.register(
        name='oidc',
        authority=authorizationUrl,
        client_id=COGNITO_CLIENT_ID,
        server_metadata_url= server_metadata_url,
        client_kwargs={'scope': 'email openid profile'}
    )
    oidc_session_initialized=True

@app.route('/')
def index():
    if oidc_session_initialized:
        user = session.get('user')
        if user:
            return  f'Hello, {user["email"]}. <a href="/logout">Logout</a>'
        else:
            return f'Welcome! Please <a href="/login">Login</a>.'
    else:
        return 'Cognito User Pool not initialized. Please check the logs'   
    
@app.route('/login')
def login():
    # Alternate option to redirect to /authorize
    # redirect_uri = url_for('authorize', _external=True)
    # return oauth.oidc.authorize_redirect(redirect_uri)
    return oauth.oidc.authorize_redirect(REDIRECT_URI)


@app.route('/authorize')
def authorize():
    token = oauth.oidc.authorize_access_token()
    user = token['userinfo']
    session['user'] = user
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)