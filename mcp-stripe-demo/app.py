# app.py
import os
from flask import Flask, session, redirect, url_for, jsonify, request
from xero_oauth import init_oauth
from xero_python.accounting import AccountingApi
from xero_python.api_client import ApiClient, Configuration
from xero_python.api_client.oauth2 import OAuth2Token
from xero_python.exceptions import AccountingBadRequestException
from xero_python.identity import IdentityApi
from xero_python.api_client import serialize 
from xero_client import save_token_and_tenant 

app = Flask(__name__)

# config (envs preferred)
app.config['SECRET_KEY']       = os.getenv('FLASK_SECRET_KEY', 'dev_only_replace_me')
app.config['XERO_CLIENT_ID']   = os.getenv('XERO_CLIENT_ID',   'YOUR_CLIENT_ID')
app.config['XERO_CLIENT_SECRET']=os.getenv('XERO_CLIENT_SECRET','YOUR_CLIENT_SECRET')
cid = app.config['XERO_CLIENT_ID'] = os.getenv('XERO_CLIENT_ID', '')
csec = app.config['XERO_CLIENT_SECRET'] = os.getenv('XERO_CLIENT_SECRET', '')

api_client = ApiClient(Configuration(
    oauth2_token=OAuth2Token(
        client_id=app.config['XERO_CLIENT_ID'],
        client_secret=app.config['XERO_CLIENT_SECRET'],
    )
))

# Tell the SDK where to GET your current token (we store it in Flask session)
@api_client.oauth2_token_getter
def _get_token_from_session():
    return session.get('token')

# Tell the SDK how to SAVE refreshed tokens (SDK will call this after refresh)
@api_client.oauth2_token_saver
def _save_token_to_session(token):
    allowed = {
        "access_token", "refresh_token", "token_type",
        "expires_in", "expires_at", "scope", "id_token"
    }
    token = {k: v for k, v in token.items() if k in allowed}
    session['token'] = token
    session.modified = True

# guard against placeholders/empties
if not cid or cid.startswith('YOUR_'):
    raise RuntimeError("XERO_CLIENT_ID not set. Export env var before running.")
if not csec or csec.startswith('YOUR_'):
    raise RuntimeError("XERO_CLIENT_SECRET not set. Export env var before running.")


# IMPORTANT: your Xero app shows this exact redirect
REDIRECT_URI = "https://localhost:8000/callback"

oauth, xero = init_oauth(app)

# minimal Xero SDK client (we'll inject token per-request)
@app.route('/')
def index():
    return "Welcome to the Xero OAuth integration app! Go to /login to connect."

@app.route('/login')
def login():
    # start the OAuth flow; pass the exact redirect URI that matches Xero settings
    return xero.authorize_redirect(redirect_uri="https://localhost:8000/callback")

@app.route('/callback')
def callback():
    token = xero.authorize_access_token() 
    allowed = {
        "access_token", "refresh_token", "token_type",
        "expires_in", "expires_at", "scope", "id_token"
    }
    token = {k: v for k, v in token.items() if k in allowed}
    session['token'] = token
    session.modified = True # no redirect_uri here
    if not token:
        return "Authorization failed", 400

    # store token so api_client’s getter can read it
    session['token'] = token

    # (optional) fetch tenants now and store one
    from xero_python.identity import IdentityApi
    identity = IdentityApi(api_client)
    conns = identity.get_connections()
    if not conns:
        return "No Xero organisations available for this user.", 400

    session['tenant_id'] = conns[0].tenant_id
    save_token_and_tenant(token, session['tenant_id'])
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    if 'token' not in session:
        return redirect(url_for('login'))
    if 'tenant_id' not in session:
        return "No tenant selected.", 400

    from xero_python.accounting import AccountingApi
    accounting = AccountingApi(api_client)
    accounts = accounting.get_accounts(session['tenant_id'])
    return {
        "tenant_id": session['tenant_id'],
        "accounts_count": len(accounts.accounts),
        "first_5": [a.name for a in accounts.accounts[:5]],
    }

@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # run EXACTLY on https://localhost:8000 to match Xero settings
    # create self-signed certs once (PowerShell):
    #   openssl genrsa -out server.key 2048
    #   openssl req -new -key server.key -out server.csr
    #   openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
    app.run(host='0.0.0.0', port=8000, debug=True, ssl_context='adhoc')
