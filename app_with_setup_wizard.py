"""
Enhanced Financial Command Center with Professional Setup Wizard
Replaces environment variable configuration with secure setup wizard
"""

import os
import sys
from flask import Flask, session, redirect, url_for, jsonify, request, render_template, send_from_directory
try:
    from flask_cors import CORS
except ImportError:
    CORS = None
from datetime import datetime
import json

# Import setup wizard functionality
from setup_wizard import SetupWizardAPI, get_configured_credentials, is_setup_required, get_integration_status

# Your existing Xero imports
from xero_oauth import init_oauth
from xero_python.accounting import AccountingApi
from xero_python.api_client import ApiClient, Configuration
from xero_python.api_client.oauth2 import OAuth2Token
from xero_python.exceptions import AccountingBadRequestException
from xero_python.identity import IdentityApi
from xero_python.api_client import serialize
from xero_client import save_token_and_tenant

# Add our security layer
sys.path.append('.')
try:
    from auth.security import SecurityManager, require_api_key, log_transaction
    SECURITY_ENABLED = True
except ImportError:
    print("⚠️  Security module not found. Running without API key authentication.")
    SECURITY_ENABLED = False
    
    # Create dummy decorators if security not available
    def require_api_key(f):
        def wrapper(*args, **kwargs):
            request.client_info = {'client_name': 'No Auth'}
            request.api_key = 'no-auth'
            return f(*args, **kwargs)
        return wrapper
    
    def log_transaction(operation, amount, currency, status):
        print(f"📊 Transaction: {operation} - {amount} {currency} - {status}")

app = Flask(__name__)

# Basic Flask configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev_only_replace_in_production')

# Initialize setup wizard API
setup_wizard_api = SetupWizardAPI()

# Enable CORS for setup API routes to support cross-origin wizard usage (e.g., file:// or different host)
if CORS is not None:
    # Allow any origin for the narrow setup API surface only
    CORS(app, resources={r"/api/setup/*": {"origins": "*"}}, supports_credentials=False)

# Initialize security manager if available
if SECURITY_ENABLED:
    security = SecurityManager()

def get_credentials_or_redirect():
    """Get credentials from setup wizard or redirect to setup if not configured"""
    credentials = get_configured_credentials()
    
    # Override with environment variables if they exist (for backward compatibility)
    env_stripe_key = os.getenv('STRIPE_API_KEY')
    env_xero_client_id = os.getenv('XERO_CLIENT_ID')
    env_xero_client_secret = os.getenv('XERO_CLIENT_SECRET')
    
    if env_stripe_key:
        credentials['STRIPE_API_KEY'] = env_stripe_key
    if env_xero_client_id:
        credentials['XERO_CLIENT_ID'] = env_xero_client_id
    if env_xero_client_secret:
        credentials['XERO_CLIENT_SECRET'] = env_xero_client_secret
    
    return credentials

def initialize_xero_client():
    """Initialize Xero API client with configured credentials"""
    credentials = get_credentials_or_redirect()
    
    xero_client_id = credentials.get('XERO_CLIENT_ID')
    xero_client_secret = credentials.get('XERO_CLIENT_SECRET')
    
    if not xero_client_id or not xero_client_secret:
        return None
        
    # Set app config for Xero
    app.config['XERO_CLIENT_ID'] = xero_client_id
    app.config['XERO_CLIENT_SECRET'] = xero_client_secret
    
    # Initialize API client
    api_client = ApiClient(Configuration(
        oauth2_token=OAuth2Token(
            client_id=xero_client_id,
            client_secret=xero_client_secret,
        )
    ))
    
    # Token handlers
    @api_client.oauth2_token_getter
    def _get_token_from_session():
        return session.get('token')

    @api_client.oauth2_token_saver
    def _save_token_to_session(token):
        allowed = {
            "access_token", "refresh_token", "token_type",
            "expires_in", "expires_at", "scope", "id_token"
        }
        token = {k: v for k, v in token.items() if k in allowed}
        session['token'] = token
        session.modified = True
    
    return api_client

# Try to initialize Xero (will be None if not configured)
api_client = initialize_xero_client()
if api_client:
    try:
        oauth, xero = init_oauth(app)
        XERO_AVAILABLE = True
    except:
        XERO_AVAILABLE = False
        print("⚠️ Xero initialization failed - configuration needed")
else:
    XERO_AVAILABLE = False
    print("⚠️ Xero not configured - setup wizard required")

# Routes

@app.route('/')
def index():
    """Enhanced home page that checks setup status"""
    if is_setup_required() and not (os.getenv('XERO_CLIENT_ID') and os.getenv('STRIPE_API_KEY')):
        return redirect(url_for('setup_wizard'))
    
    integration_status = get_integration_status()
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Financial Command Center AI</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f5f7fa; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 20px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 40px; }}
            .header h1 {{ color: #333; margin-bottom: 10px; }}
            .setup-banner {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; text-align: center; }}
            .features {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin: 30px 0; }}
            .feature {{ background: #f8f9ff; padding: 25px; border-radius: 8px; border-left: 4px solid #667eea; }}
            .status-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
            .status-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #ddd; }}
            .status-card.configured {{ border-left-color: #27ae60; background: #d4edda; }}
            .status-card.skipped {{ border-left-color: #f39c12; background: #fff3cd; }}
            .status-card.not-configured {{ border-left-color: #e74c3c; background: #f8d7da; }}
            .btn {{ background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }}
            .btn:hover {{ background: #5a6fd8; }}
            .btn-setup {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏦 Financial Command Center AI</h1>
                <p>Professional Financial Operations Platform</p>
            </div>
            
            <div class="setup-banner">
                <h3>🚀 Professional Setup Complete</h3>
                <p>Your Financial Command Center is configured and ready to use!</p>
                <a href="/setup" class="btn" style="background: rgba(255,255,255,0.2); border: 2px solid white;">⚙️ Reconfigure Settings</a>
            </div>
            
            <h3>📊 Integration Status</h3>
            <div class="status-grid">
                <div class="status-card {'configured' if integration_status.get('stripe', {}).get('configured') else 'skipped' if integration_status.get('stripe', {}).get('skipped') else 'not-configured'}">
                    <h4>💳 Stripe Integration</h4>
                    <p>Status: {'✅ Configured' if integration_status.get('stripe', {}).get('configured') else '⏭️ Skipped (Demo)' if integration_status.get('stripe', {}).get('skipped') else '❌ Not Configured'}</p>
                </div>
                
                <div class="status-card {'configured' if integration_status.get('xero', {}).get('configured') else 'skipped' if integration_status.get('xero', {}).get('skipped') else 'not-configured'}">
                    <h4>📊 Xero Integration</h4>
                    <p>Status: {'✅ Configured' if integration_status.get('xero', {}).get('configured') else '⏭️ Skipped (Demo)' if integration_status.get('xero', {}).get('skipped') else '❌ Not Configured'}</p>
                </div>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🔐 Secure Configuration</h3>
                    <p>All credentials encrypted with AES-256 and stored locally</p>
                </div>
                <div class="feature">
                    <h3>💳 Payment Processing</h3>
                    <p>Stripe integration for secure payment handling and subscriptions</p>
                </div>
                <div class="feature">
                    <h3>📊 Accounting Sync</h3>
                    <p>Xero integration for invoices, contacts, and financial data</p>
                </div>
                <div class="feature">
                    <h3>🔄 Demo Mode</h3>
                    <p>Skip services for demo purposes - configure anytime later</p>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 40px;">
                {'<a href="/login" class="btn">🔗 Connect to Xero</a>' if integration_status.get('xero', {}).get('configured') else ''}
                <a href="/admin/dashboard" class="btn">📊 Admin Dashboard</a>
                <a href="/health" class="btn">💓 Health Check</a>
                <a href="/setup" class="btn btn-setup">⚙️ Configuration</a>
            </div>
        </div>
    </body>
    </html>
    """

# Setup Wizard Routes

@app.route('/setup')
def setup_wizard():
    """Setup wizard main page"""
    return send_from_directory('templates', 'setup_wizard.html')

@app.route('/api/setup/test-stripe', methods=['POST'])
def test_stripe_api():
    """Test Stripe API connection"""
    data = request.get_json()
    result = setup_wizard_api.test_stripe_connection(data)
    return jsonify(result)

@app.route('/api/setup/test-xero', methods=['POST'])
def test_xero_api():
    """Test Xero OAuth configuration"""
    data = request.get_json()
    result = setup_wizard_api.test_xero_connection(data)
    return jsonify(result)

@app.route('/api/setup/save-config', methods=['POST'])
def save_setup_config():
    """Save setup wizard configuration"""
    data = request.get_json()
    result = setup_wizard_api.save_configuration(data)
    
    if result['success']:
        # Reinitialize the application with new configuration
        global api_client, XERO_AVAILABLE, oauth, xero
        api_client = initialize_xero_client()
        if api_client:
            try:
                oauth, xero = init_oauth(app)
                XERO_AVAILABLE = True
            except:
                XERO_AVAILABLE = False
    
    return jsonify(result)

@app.route('/api/setup/status', methods=['GET'])
def get_setup_status():
    """Get current setup status"""
    result = setup_wizard_api.get_configuration_status()
    return jsonify(result)

# Health Check

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check with integration status"""
    credentials = get_credentials_or_redirect()
    integration_status = get_integration_status()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '3.0.0',
        'security': 'enabled' if SECURITY_ENABLED else 'disabled',
        'setup_wizard': 'enabled',
        'integrations': {
            'stripe': {
                'available': bool(credentials.get('STRIPE_API_KEY')),
                'configured': integration_status.get('stripe', {}).get('configured', False),
                'skipped': integration_status.get('stripe', {}).get('skipped', False)
            },
            'xero': {
                'available': bool(credentials.get('XERO_CLIENT_ID')),
                'configured': integration_status.get('xero', {}).get('configured', False),
                'skipped': integration_status.get('xero', {}).get('skipped', False)
            }
        },
        'credentials_source': 'setup_wizard' if not os.getenv('STRIPE_API_KEY') else 'mixed'
    })

# Xero Routes (only if configured)

@app.route('/login')
def login():
    """Xero OAuth login - only if configured"""
    if not XERO_AVAILABLE:
        return jsonify({
            'error': 'Xero not configured',
            'message': 'Complete setup wizard first',
            'setup_url': url_for('setup_wizard', _external=True)
        }), 400
    return xero.authorize_redirect(redirect_uri="https://localhost:8000/callback")

@app.route('/callback')
def callback():
    """Xero OAuth callback"""
    if not XERO_AVAILABLE:
        return "Xero not configured. Complete setup wizard first.", 400
        
    try:
        token = xero.authorize_access_token()
        allowed = {
            "access_token", "refresh_token", "token_type",
            "expires_in", "expires_at", "scope", "id_token"
        }
        token = {k: v for k, v in token.items() if k in allowed}
        session['token'] = token
        session.modified = True
        
        if not token:
            return "Authorization failed", 400

        from xero_python.identity import IdentityApi
        identity = IdentityApi(api_client)
        conns = identity.get_connections()
        if not conns:
            return "No Xero organisations available for this user.", 400

        session['tenant_id'] = conns[0].tenant_id
        save_token_and_tenant(token, session['tenant_id'])
        
        if SECURITY_ENABLED:
            security.log_security_event("xero_oauth_success", "web_user", {
                "tenant_id": session['tenant_id'],
                "timestamp": datetime.now().isoformat()
            })
        
        return redirect(url_for('profile'))
    except Exception as e:
        return f"Authorization failed: {str(e)}", 400

@app.route('/profile')
def profile():
    """Xero profile page"""
    if not XERO_AVAILABLE:
        return redirect(url_for('setup_wizard'))
        
    if 'token' not in session:
        return redirect(url_for('login'))
    if 'tenant_id' not in session:
        return "No tenant selected.", 400

    try:
        accounting = AccountingApi(api_client)
        accounts = accounting.get_accounts(session['tenant_id'])
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Xero Profile - Financial Command Center</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f5f7fa; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 20px rgba(0,0,0,0.1); }}
                .account {{ background: #f8f9ff; padding: 15px; margin: 10px 0; border-radius: 6px; border-left: 4px solid #667eea; }}
                .btn {{ background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; margin: 5px; }}
                .success-banner {{ background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); padding: 20px; border-radius: 8px; margin-bottom: 30px; color: #155724; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-banner">
                    <h2>✅ Successfully Connected to Xero!</h2>
                    <p>Your accounting integration is now active and ready to use.</p>
                </div>
                
                <h1>Xero Integration Status</h1>
                <p><strong>Tenant ID:</strong> {session['tenant_id']}</p>
                <p><strong>Total Accounts:</strong> {len(accounts.accounts)}</p>
                <p><strong>Connection Status:</strong> <span style="color: #27ae60;">✅ Active</span></p>
                
                <h3>Sample Accounts (First 5):</h3>
                {''.join([f'<div class="account"><strong>{account.name}</strong><br><small>Code: {account.code}</small></div>' for account in accounts.accounts[:5]])}
                
                <div style="margin-top: 30px;">
                    <a href="/api/xero/contacts" class="btn">📋 View API Contacts</a>
                    <a href="/api/xero/invoices" class="btn">🧾 View API Invoices</a>
                    <a href="/admin/dashboard" class="btn">📊 Admin Dashboard</a>
                    <a href="/" class="btn">🏠 Home</a>
                </div>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"Error fetching profile: {str(e)}", 500

@app.route('/logout')
def logout():
    """Logout from Xero"""
    session.pop('token', None)
    session.pop('tenant_id', None)
    return redirect(url_for('index'))

# Enhanced API Endpoints

@app.route('/api/xero/contacts', methods=['GET'])
@require_api_key
def get_xero_contacts():
    """Get Xero contacts - enhanced with setup wizard integration"""
    if not XERO_AVAILABLE:
        return jsonify({
            'error': 'Xero not configured',
            'message': 'Complete setup wizard first',
            'setup_url': url_for('setup_wizard', _external=True)
        }), 400
        
    if not session.get("token"):
        return jsonify({
            'error': 'Xero not authenticated', 
            'auth_url': url_for('login', _external=True),
            'message': 'Visit the auth_url to connect Xero first'
        }), 401
    
    try:
        accounting_api = AccountingApi(api_client)
        contacts = accounting_api.get_contacts(
            xero_tenant_id=session.get('tenant_id')
        )
        
        log_transaction('xero_contacts_access', len(contacts.contacts), 'items', 'success')
        
        contacts_data = []
        for contact in contacts.contacts:
            contacts_data.append({
                'contact_id': contact.contact_id,
                'name': contact.name,
                'email': contact.email_address,
                'status': contact.contact_status.value if contact.contact_status else None,
                'is_supplier': contact.is_supplier,
                'is_customer': contact.is_customer
            })
        
        return jsonify({
            'success': True,
            'contacts': contacts_data,
            'count': len(contacts_data),
            'client': request.client_info['client_name'],
            'tenant_id': session.get('tenant_id')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stripe/payment', methods=['POST'])
@require_api_key
def create_stripe_payment():
    """Create Stripe payment - enhanced with setup wizard integration"""
    credentials = get_credentials_or_redirect()
    stripe_key = credentials.get('STRIPE_API_KEY')
    
    if not stripe_key:
        integration_status = get_integration_status()
        if integration_status.get('stripe', {}).get('skipped'):
            return jsonify({
                'error': 'Stripe in demo mode',
                'message': 'Stripe was skipped during setup - configure it to process real payments',
                'setup_url': url_for('setup_wizard', _external=True),
                'demo': True
            }), 400
        else:
            return jsonify({
                'error': 'Stripe not configured',
                'message': 'Complete setup wizard first',
                'setup_url': url_for('setup_wizard', _external=True)
            }), 400
    
    try:
        import stripe
        stripe.api_key = stripe_key
        
        data = request.get_json()
        if not data or 'amount' not in data:
            return jsonify({'error': 'amount required'}), 400
        
        amount_dollars = float(data['amount'])
        amount_cents = int(amount_dollars * 100)
        currency = data.get('currency', 'usd')
        description = data.get('description', f'Payment via {request.client_info["client_name"]}')
        
        log_transaction('stripe_payment_create', amount_dollars, currency, 'initiated')
        
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            description=description,
            automatic_payment_methods={'enabled': True}
        )
        
        log_transaction('stripe_payment_create', amount_dollars, currency, 'created')
        
        return jsonify({
            'success': True,
            'payment_intent_id': payment_intent.id,
            'client_secret': payment_intent.client_secret,
            'amount': amount_dollars,
            'currency': currency,
            'status': payment_intent.status,
            'client': request.client_info['client_name']
        })
        
    except Exception as e:
        log_transaction('stripe_payment_create', 
                       data.get('amount', 0) if 'data' in locals() else 0, 
                       data.get('currency', 'usd') if 'data' in locals() else 'usd', 
                       'failed')
        return jsonify({'error': str(e)}), 500

# Enhanced Admin Dashboard

@app.route('/admin/dashboard')
def admin_dashboard():
    """Enhanced admin dashboard with setup wizard integration"""
    if not SECURITY_ENABLED:
        return """
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial; margin: 40px;">
            <h1>⚠️ Security Module Not Available</h1>
            <p>To enable the admin dashboard and API key management:</p>
            <ol>
                <li>Create the <code>auth/security.py</code> file</li>
                <li>Install: <code>pip install cryptography</code></li>
                <li>Restart the application</li>
            </ol>
            <p><a href="/">← Back to Home</a></p>
        </body>
        </html>
        """
    
    # Load security data and integration status
    api_keys = security._load_json(security.auth_file)
    audit_log = security._load_json(security.audit_file)
    recent_events = audit_log.get('events', [])[-10:]
    integration_status = get_integration_status()
    
    dashboard_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Financial Command Center - Admin Dashboard</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-box { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
            .stat-value { font-size: 2.5em; font-weight: bold; color: #667eea; margin-bottom: 10px; }
            .stat-label { color: #666; }
            .section { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
            .integration-status { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .integration-card { padding: 20px; border-radius: 8px; border-left: 4px solid #ddd; }
            .integration-card.configured { border-left-color: #27ae60; background: #d4edda; }
            .integration-card.skipped { border-left-color: #f39c12; background: #fff3cd; }
            .integration-card.not-configured { border-left-color: #e74c3c; background: #f8d7da; }
            .btn { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }
            .btn:hover { background: #5a6fd8; }
            .api-key { border-left: 4px solid #667eea; padding: 15px; margin: 10px 0; background: #f8f9ff; }
            .event { padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 5px; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏦 Financial Command Center AI</h1>
                <p>Admin Dashboard - System Management & Monitoring</p>
            </div>
            
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-value">{{ total_keys }}</div>
                    <div class="stat-label">Total API Keys</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" style="color: #27ae60;">{{ active_keys }}</div>
                    <div class="stat-label">Active Keys</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{{ configured_services }}</div>
                    <div class="stat-label">Configured Services</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{{ recent_events|length }}</div>
                    <div class="stat-label">Recent Events</div>
                </div>
            </div>
            
            <div class="section">
                <h2>🔌 Integration Status</h2>
                <div class="integration-status">
                    <div class="integration-card {{ 'configured' if stripe_configured else 'skipped' if stripe_skipped else 'not-configured' }}">
                        <h3>💳 Stripe Integration</h3>
                        <p><strong>Status:</strong> {{ '✅ Configured & Active' if stripe_configured else '⏭️ Skipped (Demo Mode)' if stripe_skipped else '❌ Not Configured' }}</p>
                        <p><strong>Payment Processing:</strong> {{ 'Enabled' if stripe_configured else 'Demo Mode' if stripe_skipped else 'Disabled' }}</p>
                    </div>
                    
                    <div class="integration-card {{ 'configured' if xero_configured else 'skipped' if xero_skipped else 'not-configured' }}">
                        <h3>📊 Xero Integration</h3>
                        <p><strong>Status:</strong> {{ '✅ Configured & Active' if xero_configured else '⏭️ Skipped (Demo Mode)' if xero_skipped else '❌ Not Configured' }}</p>
                        <p><strong>Accounting Sync:</strong> {{ 'Enabled' if xero_configured else 'Demo Mode' if xero_skipped else 'Disabled' }}</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🔑 API Keys Management</h2>
                {% if api_keys %}
                    {% for key, info in api_keys.items() %}
                    <div class="api-key">
                        <h3>{{ info.client_name }}</h3>
                        <p><strong>API Key:</strong> <code>{{ key[:25] }}...</code></p>
                        <p><strong>Status:</strong> 
                            <span style="color: {{ '#27ae60' if info.active else '#e74c3c' }};">
                                {{ 'Active' if info.active else 'Inactive' }}
                            </span>
                        </p>
                        <p><strong>Created:</strong> {{ info.created_at }}</p>
                        <p><strong>Last Used:</strong> {{ info.last_used or 'Never' }}</p>
                        <p><strong>Permissions:</strong> {{ ', '.join(info.permissions) }}</p>
                    </div>
                    {% endfor %}
                {% else %}
                    <p>No API keys created yet.</p>
                {% endif %}
            </div>
            
            <div class="section">
                <h2>📊 Recent Activity</h2>
                {% if recent_events %}
                    {% for event in recent_events %}
                    <div class="event">
                        <strong>{{ event.timestamp[:19] }}</strong> - 
                        {{ event.event_type }} by {{ event.client_name }}
                        {% if event.details %}
                        <br><small>{{ event.details }}</small>
                        {% endif %}
                    </div>
                    {% endfor %}
                {% else %}
                    <p>No recent activity.</p>
                {% endif %}
            </div>
            
            <div class="section">
                <h2>🚀 Quick Actions</h2>
                <a href="/setup" class="btn">⚙️ Configuration Wizard</a>
                <a href="/health" class="btn">💓 Health Check</a>
                {% if xero_configured %}
                <a href="/login" class="btn">🔗 Connect Xero</a>
                {% endif %}
                <a href="/admin/create-demo-key" class="btn">🔑 Create Demo Key</a>
                <a href="/" class="btn">🏠 Home</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Calculate stats
    total_keys = len(api_keys)
    active_keys = sum(1 for info in api_keys.values() if info.get('active', False))
    configured_services = sum([
        integration_status.get('stripe', {}).get('configured', False),
        integration_status.get('xero', {}).get('configured', False)
    ])
    
    from jinja2 import Template
    template = Template(dashboard_html)
    
    return template.render(
        api_keys=api_keys,
        total_keys=total_keys,
        active_keys=active_keys,
        configured_services=configured_services,
        recent_events=recent_events,
        stripe_configured=integration_status.get('stripe', {}).get('configured', False),
        stripe_skipped=integration_status.get('stripe', {}).get('skipped', False),
        xero_configured=integration_status.get('xero', {}).get('configured', False),
        xero_skipped=integration_status.get('xero', {}).get('skipped', False)
    )

@app.route('/admin/create-demo-key')
def create_demo_key():
    """Create demo API key via web interface"""
    if not SECURITY_ENABLED:
        return "Security module not available. Install cryptography and create auth/security.py", 500
    
    demo_key = security.generate_api_key("Web Demo Client", ["read", "write"])
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Demo API Key Created</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f5f7fa; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 20px rgba(0,0,0,0.1); }}
            .key-box {{ background: #e8f5e8; padding: 20px; border-radius: 8px; border: 1px solid #c3e6cb; margin: 20px 0; }}
            .code {{ background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: 'Courier New', monospace; margin: 10px 0; overflow-x: auto; font-size: 14px; }}
            .btn {{ background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔑 Demo API Key Created!</h1>
            
            <div class="key-box">
                <h3>Your New API Key:</h3>
                <div class="code">{demo_key}</div>
                <p><strong>⚠️ Important:</strong> Save this key securely - it won't be shown again!</p>
            </div>
            
            <h3>🧪 Test Your API Key:</h3>
            
            <h4>1. Test Authentication:</h4>
            <div class="code">
curl -H "X-API-Key: {demo_key}" https://localhost:8000/api/ping
            </div>
            
            <h4>2. Get Health Status:</h4>
            <div class="code">
curl -H "X-API-Key: {demo_key}" https://localhost:8000/health
            </div>
            
            <div style="margin-top: 30px;">
                <a href="/admin/dashboard" class="btn">← Back to Dashboard</a>
                <a href="/setup" class="btn">⚙️ Configuration Wizard</a>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("🚀 Starting Financial Command Center with Setup Wizard...")
    print("=" * 60)
    print(f"🔐 Security: {'Enabled' if SECURITY_ENABLED else 'Disabled'}")
    print(f"⚙️ Setup Wizard: Enabled")
    print(f"📊 Xero: {'Available' if XERO_AVAILABLE else 'Needs Configuration'}")
    
    credentials = get_credentials_or_redirect()
    print(f"💳 Stripe: {'Configured' if credentials.get('STRIPE_API_KEY') else 'Needs Setup'}")
    
    # Initialize SSL certificate management
    try:
        from cert_manager import CertificateManager
        from server_modes import configure_server_mode
        
        cert_manager = CertificateManager()
        ssl_context = None
        server_mode = "HTTPS"
        
        # Configure server mode management
        configure_server_mode(app)
        
        # Check SSL mode preference
        force_https = os.getenv('FORCE_HTTPS', 'true').lower() == 'true'
        allow_http = os.getenv('ALLOW_HTTP', 'false').lower() == 'true'
        
        if force_https or not allow_http:
            # HTTPS mode - generate certificates if needed
            print("🔐 HTTPS Mode - Ensuring SSL certificates...")
            cert_generated = cert_manager.ensure_certificates()
            ssl_context = cert_manager.get_ssl_context()
            
            if cert_generated:
                print("✨ New SSL certificates generated!")
                print("📦 To eliminate browser warnings, install the CA certificate:")
                print(f"   python cert_manager.py --bundle")
        else:
            # HTTP mode with warnings
            server_mode = "HTTP (with HTTPS upgrade prompts)"
            print("⚠️  HTTP Mode - Running without SSL encryption")
            print("   Set FORCE_HTTPS=true for production use")
    
    except ImportError as e:
        print("⚠️  SSL Certificate Manager not available - using Flask's adhoc SSL")
        print(f"   Install missing dependencies: {e}")
        ssl_context = 'adhoc'
    
    print()
    print("📋 Available endpoints:")
    print("  GET  / - Smart home page (redirects to setup if needed)")
    print("  GET  /setup - Professional setup wizard")
    print("  GET  /health - Enhanced health check")
    
    if SECURITY_ENABLED:
        print("  🔑 Security Endpoints: /api/ping, /api/create-key, /api/key-stats")
    
    print("  📊 Admin: /admin/dashboard")
    print("  💳 Stripe: /api/stripe/payment")
    print("  🔧 SSL Help: /admin/ssl-help")
    print("  📦 Certificate Bundle: /admin/certificate-bundle")
    
    if XERO_AVAILABLE:
        print("  🔗 Xero: /login, /callback, /profile, /api/xero/contacts, /api/xero/invoices")
    else:
        print("  🔗 Xero: Configure via setup wizard")
    
    print()
    protocol = "https" if ssl_context else "http"
    port = 8000
    print("🌐 URLs:")
    print(f"  🏠 Home: {protocol}://localhost:{port}/")
    print(f"  ⚙️ Setup: {protocol}://localhost:{port}/setup")
    print(f"  🎛️  Admin: {protocol}://localhost:{port}/admin/dashboard")
    print(f"  🔧 SSL Help: {protocol}://localhost:{port}/admin/ssl-help")
    print()
    
    if is_setup_required() and not os.getenv('STRIPE_API_KEY'):
        print("🎯 FIRST TIME SETUP:")
        print(f"   Visit {protocol}://localhost:{port}/setup to configure your integrations")
        print(f"   Or {protocol}://localhost:{port}/ to start the guided setup")
        print()
    
    print(f"🔒 Server Mode: {server_mode}")
    if ssl_context and ssl_context != 'adhoc':
        print("📜 SSL Certificate Status:")
        try:
            health = cert_manager.health_check()
            print(f"   ✅ Certificate Valid: {health['certificate_valid']}")
            print(f"   📅 Expires: {health['expires']}")
            print(f"   🏷️  Hostnames: {', '.join(health['hostnames'])}")
            if not health['certificate_valid']:
                print("   🔄 Certificates will be regenerated automatically")
        except Exception as e:
            print(f"   ⚠️  Certificate check failed: {e}")
    
    print()
    print("🔥 Professional Financial Command Center ready!")
    
    # Start the Flask application
    if ssl_context:
        app.run(host='localhost', port=port, debug=True, ssl_context=ssl_context)
    else:
        # HTTP mode
        app.run(host='localhost', port=port, debug=True)
