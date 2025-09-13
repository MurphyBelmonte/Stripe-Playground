from datetime import datetime, timedelta


ACCOUNTS = [
    {
        "account_id": "demo_checking_123",
        "name": "Business Checking",
        "type": "depository",
        "subtype": "checking",
        "mask": "0000",
        "balances": {"available": 24750.15, "current": 25430.75, "iso_currency_code": "USD"},
        "official_name": "Basic Business Checking",
        "institution": "First National Bank",
    },
    {
        "account_id": "demo_savings_456",
        "name": "Business Savings",
        "type": "depository",
        "subtype": "savings",
        "mask": "1111",
        "balances": {"available": 85200.50, "current": 85200.50, "iso_currency_code": "USD"},
        "official_name": "Business Savings",
        "institution": "First National Bank",
    },
]


_today = datetime.utcnow().date()

TRANSACTIONS = [
    {
        "transaction_id": "txn_demo_001",
        "account_id": "demo_checking_123",
        "date": (_today - timedelta(days=1)).isoformat(),
        "name": "Stripe Payout",
        "amount": -1450.32,
        "iso_currency_code": "USD",
        "pending": False,
        "category": ["Transfer", "Credit"],
    },
    {
        "transaction_id": "txn_demo_002",
        "account_id": "demo_checking_123",
        "date": (_today - timedelta(days=2)).isoformat(),
        "name": "AWS",
        "amount": 235.88,
        "iso_currency_code": "USD",
        "pending": False,
        "category": ["Service", "Hosting"],
    },
    {
        "transaction_id": "txn_demo_003",
        "account_id": "demo_savings_456",
        "date": (_today - timedelta(days=3)).isoformat(),
        "name": "Interest Payment",
        "amount": -12.04,
        "iso_currency_code": "USD",
        "pending": False,
        "category": ["Interest"],
    },
]

