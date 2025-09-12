# Financial Command Center (MCP Integrations)

This repo (`Financial Command Center`) contains a **Modular Command Protocol (MCP) integration suite** that unifies:

- **Stripe** → payments, customers, subscriptions, checkout  
- **Plaid** → banking data, balances, transactions (sandbox + real)  
- **Xero** → accounting, contacts, invoices, reporting  
- **Compliance** → audit logging, blacklist, transaction scanning  

It enables natural-language control of real financial workflows via Claude Desktop (or any MCP client).

---

## ✨ Features

### 🔹 Xero MCP
- Contacts: `xero_list_contacts`, `xero_create_contact`, `xero_find_contact`
- Invoices: `xero_list_invoices`, `xero_create_invoice`, `xero_delete_draft_invoice`
- Exporting: `xero_get_invoice_pdf`, `xero_export_invoices_csv`
- Dashboard: `xero_dashboard`, `xero_org_info`, `xero_set_tenant`

### 🔹 Stripe MCP
- Payments: `process_payment`, `check_payment_status`, `process_refund`, `capture_payment_intent`, `cancel_payment_intent`
- Customers & Payment Methods: `create_customer`, `create_setup_intent`, `list_payment_methods`, `attach_payment_method`, `detach_payment_method`
- Products & Subscriptions: `create_product`, `create_price`, `create_checkout_session`, `create_subscription`, `cancel_subscription`
- Reporting: `list_payments`, `retrieve_charge`, `retrieve_refund`
- Webhooks: `verify_webhook`
- Utility: `ping`

### 🔹 Plaid MCP
- Linking: `link_token_create`, `sandbox_public_token_create`, `item_public_token_exchange`
- Accounts & balances: `accounts_and_balances`
- Transactions: `transactions_get` (date-safe)
- Bank details & identity: `auth_get`, `identity_get`
- Maintenance: `remove_item`
- Server helper: `verify_plaid_webhook`

### 🔹 Compliance MCP
- Status: `info`
- Config: `config_set`
- Blacklist: `blacklist_add`, `blacklist_list`
- Scan: `scan_plaid_transactions` (normalizes merchants, filters, checks blacklist, writes JSON report, adds audit log)
- Audit: `audit_log_tail`
- Stripe helper: `stripe_payment_intent_status`
- Server helper: `verify_plaid_webhook`

---

## 📋 Prerequisites
- [Xero Developer Account](https://developer.xero.com/)
- [Stripe Account](https://stripe.com/)
- [Plaid Account](https://my.plaid.com/sign-in)

## 🛠️ Setup

### 1) Clone Repo
```bash
git clone https://github.com/MurphyBelmonte/mcp-stripe-demo.git
cd mcp-stripe-demo
```
### 2) Create & activate venv
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```
### 3) Install dependencies
```bash
pip install -r requirements.txt
```
### 4) Configure environment variables (Windows Powershell)
- Xero 
```bash
$env:XERO_CLIENT_ID=your_xero_client_id
$env:XERO_CLIENT_SECRET=your_xero_client_secret
$env:FLASK_SECRET_KEY=dev
```
- Stripe
```bash
$env:STRIPE_API_KEY=sk_test_...
$env:STRIPE_DEFAULT_CURRENCY=usd
$env:MCP_STRIPE_PROD=false
```
- Plaid
```bash
$env:PLAID_CLIENT_ID=your_plaid_client_id
$env:PLAID_SECRET=your_plaid_secret
$env:PLAID_ENV=sandbox
```
### 5) Authenticate with Xero (once)
```bash
python app.py
```
- Open the generated link `'https://localhost:8000' (example)`
- Click on `Advanced` at the bottom left of the web page
- Then click on `'Proceed to localhost (unsafe)'`
- You should see a welcome text and an instruction to go to `'/login'`
- Attach `'/login'`and open `'https://localhost:8000/login'`
- Xero login page should appear, login and grant access to your account
- A 'tenant_id' will be generated. Now you can close the browser
- Open claude desktop and in the `search an tools` option, you'll be able to see the mcp server
- You can also run each server [separately](#run-mcp-servers)
- Now test with [Prompts](#example-prompts)

## Run MCP servers
- Windows PowerShell
```bash
& "C:\Users\Hi\.local\bin\uv.EXE" run --project . mcp run xero_mcp.py
& "C:\Users\Hi\.local\bin\uv.EXE" run --project . mcp run stripe_mcp.py
& "C:\Users\Hi\.local\bin\uv.EXE" run --project . mcp run plaid_mcp.py
& "C:\Users\Hi\.local\bin\uv.EXE" run --project . mcp run compliance_mcp.py
```
- MacOS/Linux
```bash
uv run --project . mcp run xero_mcp.py
uv run --project . mcp run stripe_mcp.py
uv run --project . mcp run plaid_mcp.py
uv run --project . mcp run compliance_mcp.py
```
## 🖥️ Claude Desktop Config (snippet)
```json
{
  "mcpServers": {
    "xero-mcp": {
      "command": "C:\\Users\\Hi\\.local\\bin\\uv.EXE",
      "args": [
        "run", "--project",
        "C:\\Users\\Hi\\Documents\\GitHub\\Stripe Playground\\mcp-stripe-demo",
        "mcp", "run",
        "C:\\Users\\Hi\\Documents\\GitHub\\Stripe Playground\\mcp-stripe-demo\\xero_mcp.py"
      ],
      "env": {
        "XERO_CLIENT_ID": "your_xero_client_id",
        "XERO_CLIENT_SECRET": "your_xero_client_secret",
        "FLASK_SECRET_KEY": "dev"
      }
    },
    "plaid-integration": {
      "command": "C:\\Users\\Hi\\.local\\bin\\uv.EXE",
      "args": [
        "run", "--project",
        "C:\\Users\\Hi\\Documents\\GitHub\\Stripe Playground\\mcp-stripe-demo",
        "mcp", "run",
        "C:\\Users\\Hi\\Documents\\GitHub\\Stripe Playground\\mcp-stripe-demo\\plaid_mcp.py"
      ],
      "env": {
        "PLAID_CLIENT_ID": "your_plaid_client_id",
        "PLAID_SECRET": "your_plaid_secret",
        "PLAID_ENV": "sandbox"
      }
    },
    "compliance-suite": {
      "command": "C:\\Users\\Hi\\.local\\bin\\uv.EXE",
      "args": [
        "run", "--project",
        "C:\\Users\\Hi\\Documents\\GitHub\\Stripe Playground\\mcp-stripe-demo",
        "mcp", "run",
        "C:\\Users\\Hi\\Documents\\GitHub\\Stripe Playground\\mcp-stripe-demo\\compliance_mcp.py"
      ],
      "env": {
        "STRIPE_API_KEY": "sk_test_...",
        "PLAID_CLIENT_ID": "your_plaid_client_id",
        "PLAID_SECRET": "your_plaid_secret",
        "PLAID_ENV": "sandbox"
      }
    }
  }
}
```
##  Example Prompts
### Xero: 
- `Check my Xero authentication status with   xero_whoami.` 
- `Run xero_org_info and show org name, tenant_id, and base currency.` 
- `List the first 10 contacts using xero_list_contacts(limit=10).` 
- `Create a draft invoice for Bank West: 2 hours at 150.` 
- `Get the PDF for invoice INV-0005.` `Export the last 50 ACCREC invoices to CSV.`

### Stripe: 
- `Run stripe ping.` 
- `Create a $25.50 test payment for "Starter plan" and confirm now.` 
- `Refund PaymentIntent pi_123 in full.` 
- `Authorize $100 (manual capture), then capture $60.` 
- `Create a Pro Plan product, $29/month price, and subscription for customer cus_123.`

### Plaid: 
- `Create a sandbox public token then exchange it and save as "demo2".` 
- `Show accounts and balances for "demo2".` 
- `List last 30 days transactions for "demo2".`
-  `Get ACH details for "demo2".`

### Compliance: 
- `Show compliance info.` 
- `Set min flag amount to 1000 USD and exclude pending.` 
- `Blacklist merchant "Coffee Shop".` 
- `Scan Plaid transactions for demo2, last 30 days, min 1000, exclude pending.` 
- `Show last 50 audit events.`


## 📹 Demo Script (2–3 min)
- `xero_whoami` → confirm auth 
- `xero_list_contacts(limit=5)`
- `xero_create_invoice(contact_name="Bank West", quantity=2, unit_amount=150)`
- `xero_list_invoices(kind="ACCREC", status="DRAFT", limit=5)`
- `xero_get_invoice_pdf(invoice_number="INV-XXXX")`
- `process_payment(amount_dollars=10, description="Test", confirm_now=true)`
- `sandbox_public_token_create` → `item_public_token_exchange` → `accounts_and_balances(key="demo2")`
- `transactions_get(key="demo2", days=30)`
- `scan_plaid_transactions(key="demo2", days=30, min_amount=1000, include_pending=false)`
- `xero_dashboard`→ unified view; show generated PDF/CSV in `exports/`

## 🔒 Security
- Never commit secrets: `.venv/`, `tokens/`, `exports/`, `plaid_store.json`, `__pycache__/` should be in `.gitignore`.
- Use test/sandbox keys for demos.
- Always verify webhooks (`verify_webhook` for Stripe; `verify_plaid_webhook` for Plaid).
- Compliance logs and reports contain sensitive data — treat carefully.


