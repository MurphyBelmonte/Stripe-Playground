from datetime import datetime, timedelta


CONTACTS = [
    {
        "contact_id": "demo-contact-001",
        "name": "Acme Supplies Co.",
        "email": "billing@acmesupplies.example",
        "status": "ACTIVE",
        "is_supplier": True,
        "is_customer": False,
    },
    {
        "contact_id": "demo-contact-002",
        "name": "Brightside Marketing LLC",
        "email": "ap@brightside.example",
        "status": "ACTIVE",
        "is_supplier": False,
        "is_customer": True,
    },
    {
        "contact_id": "demo-contact-003",
        "name": "Northwind Traders",
        "email": "accounts@northwind.example",
        "status": "ACTIVE",
        "is_supplier": False,
        "is_customer": True,
    },
]


_today = datetime.utcnow().date()
_d = lambda n: (_today - timedelta(days=n)).isoformat()

INVOICES = [
    {
        "invoice_id": "demo-inv-1001",
        "invoice_number": "INV-1001",
        "type": "ACCREC",
        "status": "AUTHORISED",
        "total": 1250.00,
        "currency_code": "USD",
        "date": _d(28),
        "due_date": _d(10),
        "contact_name": "Brightside Marketing LLC",
    },
    {
        "invoice_id": "demo-inv-1002",
        "invoice_number": "INV-1002",
        "type": "ACCREC",
        "status": "DRAFT",
        "total": 980.00,
        "currency_code": "USD",
        "date": _d(7),
        "due_date": _d(-7),
        "contact_name": "Northwind Traders",
    },
    {
        "invoice_id": "demo-inv-2001",
        "invoice_number": "BILL-2001",
        "type": "ACCPAY",
        "status": "SUBMITTED",
        "total": 430.25,
        "currency_code": "USD",
        "date": _d(14),
        "due_date": _d(0),
        "contact_name": "Acme Supplies Co.",
    },
]


PROFIT_AND_LOSS = {
    "report": "Profit and Loss",
    "period": {
        "from": (_today.replace(day=1)).isoformat(),
        "to": _today.isoformat(),
    },
    "currency": "USD",
    "totals": {
        "revenue": 48500.00,
        "cost_of_goods_sold": 22500.00,
        "gross_profit": 26000.00,
        "operating_expenses": 14500.00,
        "net_profit": 11500.00,
    },
    "lines": [
        {"category": "Revenue", "name": "Product Sales", "amount": 41000.00},
        {"category": "Revenue", "name": "Service Income", "amount": 7500.00},
        {"category": "COGS", "name": "Inventory Purchases", "amount": 19800.00},
        {"category": "COGS", "name": "Shipping & Fulfillment", "amount": 2700.00},
        {"category": "OPEX", "name": "Salaries & Wages", "amount": 8900.00},
        {"category": "OPEX", "name": "Marketing", "amount": 2500.00},
        {"category": "OPEX", "name": "Software & Subscriptions", "amount": 1100.00},
        {"category": "OPEX", "name": "Utilities", "amount": 450.00},
        {"category": "OPEX", "name": "Office Supplies", "amount": 350.00},
        {"category": "OPEX", "name": "Other", "amount": 1200.00},
    ],
}

