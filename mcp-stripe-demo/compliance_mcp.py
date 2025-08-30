# compliance_mcp.py
import os, json, csv, time, hashlib, pathlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from functools import wraps


from mcp.server.fastmcp import FastMCP

# 3rd party sdks you already use
import stripe
import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest

# ---------- App ----------
app = FastMCP("compliance-suite")

ROOT = pathlib.Path(__file__).resolve().parent
REPORTS_DIR = ROOT / "reports"
AUDIT_DIR   = ROOT / "audit"
STORE_FILE  = ROOT / "plaid_store.json"            # reused from your Plaid server
CONF_FILE   = ROOT / "compliance_config.json"
BLACKLIST   = ROOT / "compliance_blacklist.json"
ALERTS_FILE = ROOT / "alerts.jsonl"
AUDIT_LOG   = AUDIT_DIR / "audit_log.jsonl"
STORE_PATH = os.path.join(os.path.dirname(__file__), "plaid_store.json")

REPORTS_DIR.mkdir(exist_ok=True)
AUDIT_DIR.mkdir(exist_ok=True)

# ---------- Config (editable via tools) ----------
DEFAULT_CONF: Dict[str, Any] = {
    # Stripe
    "stripe_high_amount_cents": 20_000,     # $200
    "stripe_currency_allowlist": ["usd"],
    "stripe_velocity_24h_limit": 5,         # per customer/payment_method
    # Plaid
    "plaid_high_amount_usd": 500.0,
    "plaid_velocity_24h_limit": 20,
    # Alerts / Risk
    "risk_threshold_alert": 70,             # 0-100 -> write to alerts.jsonl
}

def _load_store() -> Dict[str, Any]:
    if not os.path.exists(STORE_PATH):
        return {}
    with open(STORE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_store(d: Dict[str, Any]) -> None:
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)

def _token_for(alias_or_token: str) -> str:
    """
    Accepts either an alias saved in plaid_store.json or a raw token.
    If it's not an alias we recognize, just pass it through unchanged.
    """
    if alias_or_token.startswith(("access-", "public-")):
        return alias_or_token
    store = _load_store()
    return store.get("items", {}).get(alias_or_token, {}).get("access_token") or alias_or_token

def _load_json(path: pathlib.Path, default: Any) -> Any:
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return default

def _save_json(path: pathlib.Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _conf() -> Dict[str, Any]:
    return _load_json(CONF_FILE, DEFAULT_CONF.copy())

def _save_conf(d: Dict[str, Any]) -> None:
    base = DEFAULT_CONF.copy()
    base.update(d)
    _save_json(CONF_FILE, base)

def _blacklist() -> Dict[str, List[str]]:
    return _load_json(BLACKLIST, {"merchant_names": [], "mccs": []})

def _save_blacklist(d: Dict[str, List[str]]) -> None:
    _save_json(BLACKLIST, d)

# ---------- Audit / Alerts ----------
def _audit_write(entry: Dict[str, Any]) -> None:
    entry["ts"] = datetime.utcnow().isoformat() + "Z"
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def _alert_write(entry: Dict[str, Any]) -> None:
    entry["ts"] = datetime.utcnow().isoformat() + "Z"
    with ALERTS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def audited(tool_fn):
    @wraps(tool_fn)
    def wrapper(*args, **kwargs):
        try:
            res = tool_fn(*args, **kwargs)
            _audit_write({"tool": tool_fn.__name__, "args": _redact(kwargs), "ok": True})
            return res
        except Exception as e:
            _audit_write({"tool": tool_fn.__name__, "args": _redact(kwargs), "ok": False, "error": str(e)})
            raise
    return wrapper

def _redact(d: Dict[str, Any]) -> Dict[str, Any]:
    # mask tokens/ids-ish
    out = {}
    for k, v in (d or {}).items():
        if v is None:
            out[k] = None
            continue
        s = str(v)
        if any(key in k.lower() for key in ["token", "secret", "key"]):
            out[k] = s[:6] + "…" if len(s) > 6 else "****"
        else:
            out[k] = v
    return out

# ---------- Stripe client ----------
def _stripe() -> None:
    key = os.environ.get("STRIPE_API_KEY")
    if not key:
        raise RuntimeError("Set STRIPE_API_KEY in the environment.")
    stripe.api_key = key

# ---------- Plaid client ----------
def _plaid_host():
    env = os.environ.get("PLAID_ENV", "sandbox").lower()
    if env == "production":
        return getattr(plaid.Environment, "Production", plaid.Environment.Sandbox)
    if env == "development":
        return getattr(plaid.Environment, "Development", getattr(plaid.Environment, "Sandbox", plaid.Environment.Production))
    return getattr(plaid.Environment, "Sandbox", plaid.Environment.Production)

def _resolve_host():
    env = os.environ.get("PLAID_ENV", "sandbox").lower()
    if env == "production":
        return getattr(plaid.Environment, "Production", plaid.Environment.Sandbox)
    if env == "development":
        return getattr(plaid.Environment, "Development", getattr(plaid.Environment, "Sandbox", plaid.Environment.Production))
    return getattr(plaid.Environment, "Sandbox", plaid.Environment.Production)

def _plaid_client() -> plaid_api.PlaidApi:
    cid = os.environ.get("PLAID_CLIENT_ID")
    sec = os.environ.get("PLAID_SECRET")
    if not cid or not sec:
        raise RuntimeError("Set PLAID_CLIENT_ID and PLAID_SECRET in the environment.")
    cfg = plaid.Configuration(
        host=_resolve_host(),
        api_key={"clientId": cid, "secret": sec},
    )
    return plaid_api.PlaidApi(plaid.ApiClient(cfg))

def _plaid_token_for(alias_or_token: str) -> str:
    # read same file your Plaid server uses
    if alias_or_token.startswith(("access-", "public-")):
        return alias_or_token
    if STORE_FILE.exists():
        store = json.loads(STORE_FILE.read_text(encoding="utf-8"))
        return store.get("items", {}).get(alias_or_token, {}).get("access_token") or alias_or_token
    return alias_or_token

# ---------- Risk scoring helpers ----------
def _score_reasons_to_score(reasons: List[str]) -> int:
    # very simple: each reason +20; clamp 0..100
    score = min(100, 20 * len(reasons))
    return score

def _stripe_risk_for_pi(pi: Dict[str, Any], conf: Dict[str, Any], bl: Dict[str, List[str]]) -> Tuple[int, List[str]]:
    reasons = []
    amount = int(pi.get("amount", 0))
    currency = (pi.get("currency") or "").lower()
    if amount >= conf["stripe_high_amount_cents"]:
        reasons.append(f"high_amount:{amount}")
    if conf["stripe_currency_allowlist"] and currency not in [c.lower() for c in conf["stripe_currency_allowlist"]]:
        reasons.append(f"currency_not_allowed:{currency}")

    # charge-level hints
    charges = pi.get("charges", {}).get("data", []) if isinstance(pi.get("charges"), dict) else []
    if charges:
        ch = charges[0]
        outcome = (ch.get("outcome") or {})
        risk_level = (outcome.get("risk_level") or "").lower()
        if risk_level in {"highest", "elevated"}:
            reasons.append(f"stripe_outcome_risk:{risk_level}")
        fd = ch.get("fraud_details") or {}
        if fd.get("user_report") or fd.get("stripe_report"):
            reasons.append("fraud_reported")

        mname = (ch.get("payment_method_details", {}) or {}).get("card", {}) or {}
        brand = mname.get("brand")
        if brand and str(brand).lower() in [b.lower() for b in bl.get("merchant_names", [])]:
            reasons.append(f"brand_blacklisted:{brand}")

    return _score_reasons_to_score(reasons), reasons

def _plaid_risk_for_tx(tx: Dict[str, Any], conf: Dict[str, Any], bl: Dict[str, List[str]]) -> Tuple[int, List[str]]:
    reasons = []
    amt = abs(float(tx.get("amount") or 0.0))
    if amt >= float(conf["plaid_high_amount_usd"]):
        reasons.append(f"high_amount_usd:{amt}")
    name = (tx.get("name") or "").lower()
    if any(b.lower() in name for b in bl.get("merchant_names", [])):
        reasons.append("merchant_blacklisted")
    # category heuristic
    cats = tx.get("category") or []
    cats_l = [str(c).lower() for c in cats]
    if "cash advance" in cats_l or "fraudulent" in cats_l:
        reasons.append("category_flag")
    return _score_reasons_to_score(reasons), reasons

def _write_csv(path: pathlib.Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = sorted({k for r in rows for k in r.keys()})
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)

# ---------- Tools: config / blacklist / audit ----------
@app.tool()
@audited
def compliance_config_get() -> Dict[str, Any]:
    """Return current compliance configuration."""
    return _conf()

@app.tool()
@audited
def compliance_config_set(
    stripe_high_amount_cents: Optional[int] = None,
    stripe_currency_allowlist: Optional[List[str]] = None,
    stripe_velocity_24h_limit: Optional[int] = None,
    plaid_high_amount_usd: Optional[float] = None,
    plaid_velocity_24h_limit: Optional[int] = None,
    risk_threshold_alert: Optional[int] = None,
) -> Dict[str, Any]:
    """Update parts of the compliance configuration."""
    c = _conf()
    if stripe_high_amount_cents is not None: c["stripe_high_amount_cents"] = int(stripe_high_amount_cents)
    if stripe_currency_allowlist is not None: c["stripe_currency_allowlist"] = list(stripe_currency_allowlist)
    if stripe_velocity_24h_limit is not None: c["stripe_velocity_24h_limit"] = int(stripe_velocity_24h_limit)
    if plaid_high_amount_usd is not None: c["plaid_high_amount_usd"] = float(plaid_high_amount_usd)
    if plaid_velocity_24h_limit is not None: c["plaid_velocity_24h_limit"] = int(plaid_velocity_24h_limit)
    if risk_threshold_alert is not None: c["risk_threshold_alert"] = int(risk_threshold_alert)
    _save_conf(c)
    return c

@app.tool()
@audited
def blacklist_add(merchant_names: Optional[List[str]] = None, mccs: Optional[List[str]] = None) -> Dict[str, Any]:
    """Add merchant names or MCCs to blacklist."""
    bl = _blacklist()
    if merchant_names:
        for n in merchant_names:
            if n not in bl["merchant_names"]: bl["merchant_names"].append(n)
    if mccs:
        for m in mccs:
            if m not in bl["mccs"]: bl["mccs"].append(m)
    _save_blacklist(bl)
    return bl

@app.tool()
@audited
def blacklist_list() -> Dict[str, Any]:
    """Return blacklist."""
    return _blacklist()

@app.tool()
@audited
def audit_tail(lines: int = 50) -> Dict[str, Any]:
    """Show last N audit entries."""
    if not AUDIT_LOG.exists(): return {"audit": []}
    with AUDIT_LOG.open("r", encoding="utf-8") as f:
        rows = f.read().splitlines()[-max(1, lines):]
        return {"audit": [json.loads(r) for r in rows]}

@app.tool()
@audited
def alerts_tail(lines: int = 50) -> Dict[str, Any]:
    """Show last N alerts (high-risk findings)."""
    if not ALERTS_FILE.exists(): return {"alerts": []}
    with ALERTS_FILE.open("r", encoding="utf-8") as f:
        rows = f.read().splitlines()[-max(1, lines):]
        return {"alerts": [json.loads(r) for r in rows]}

# ---------- Tools: Stripe scanning ----------
@app.tool()
@audited
def scan_stripe_payments(days: int = 30, limit: int = 200) -> Dict[str, Any]:
    """
    Pull recent PaymentIntents from Stripe and score for risk.
    Creates CSV/JSON in /reports and returns a summary.
    """
    _stripe()
    conf = _conf()
    bl   = _blacklist()

    since = int(time.time()) - max(1, days) * 86400
    items: List[Dict[str, Any]] = []
    high: List[Dict[str, Any]] = []

    # paginate PaymentIntents
    starting_after = None
    fetched = 0
    while True:
        resp = stripe.PaymentIntent.list(
            created={"gte": since},
            limit=min(100, max(1, limit - fetched)),
            starting_after=starting_after
        )
        data = resp.get("data", [])
        if not data: break
        for pi in data:
            d = pi.to_dict() if hasattr(pi, "to_dict") else dict(pi)
            score, reasons = _stripe_risk_for_pi(d, conf, bl)
            row = {
                "payment_intent": d.get("id"),
                "amount": d.get("amount"),
                "currency": d.get("currency"),
                "status": d.get("status"),
                "created": d.get("created"),
                "risk_score": score,
                "reasons": ";".join(reasons),
            }
            items.append(row)
            if score >= conf["risk_threshold_alert"]:
                _alert_write({"source": "stripe", **row})
                high.append(row)
        fetched += len(data)
        if fetched >= limit or not resp.get("has_more"): break
        starting_after = data[-1]["id"]

    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    csv_path  = REPORTS_DIR / f"stripe_report_{ts}.csv"
    json_path = REPORTS_DIR / f"stripe_report_{ts}.json"
    _write_csv(csv_path, items)
    json_path.write_text(json.dumps(items, indent=2), encoding="utf-8")

    return {
        "count": len(items),
        "high_risk": len(high),
        "report_csv": str(csv_path),
        "report_json": str(json_path),
        "sample": items[:5],
    }

# ---------- Tools: Plaid scanning ----------
@app.tool()
@audited
def plaid_transactions_scan(
    key: str,
    days: int = 30,
    count: int = 50,
    offset: int = 0,
) -> dict:
    """
    Compliance scan: fetch recent transactions from Plaid.
    - Accepts an alias or raw access token in `key`
    - Uses date objects first; falls back to ISO strings if your SDK wants those
    """
    client = _plaid_client()
    access_token = _token_for(key)

    # Build proper date objects
    end_dt = date.today()
    start_dt = end_dt - timedelta(days=max(1, int(days)))

    # Always build options as proper model types
    opts = TransactionsGetRequestOptions(count=int(count), offset=int(offset))

    used_encoding = "date_objects"
    try:
        # Preferred: pass date objects (most modern plaid-python builds expect this)
        req = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_dt,
            end_date=end_dt,
            options=opts,
        )
        resp = client.transactions_get(req)
    except Exception as e:
        msg = str(e)
        # If your local plaid SDK is the variant that expects strings, fall back automatically
        needs_string = ("Required value type is str" in msg) or ("passed type was date at ['start_date']" in msg)
        if needs_string:
            used_encoding = "iso_strings_fallback"
            req = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_dt.isoformat(),
                end_date=end_dt.isoformat(),
                options=opts,
            )
            resp = client.transactions_get(req)
        else:
            # Re-raise anything unrelated to type expectations
            raise

    data = resp.to_dict()
    tx = []
    for t in data.get("transactions", []):
        tx.append({
            "tx_id": t.get("transaction_id"),
            "account_id": t.get("account_id"),
            "date": t.get("date"),
            "name": t.get("name"),
            "amount": t.get("amount"),
            "category": t.get("category"),
            "pending": t.get("pending"),
        })

    return {
        "request_dates": {
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "encoding_used": used_encoding,  # helps confirm which branch was taken
        },
        "total": data.get("total_transactions", len(tx)),
        "transactions": tx,
    }

# ---------- Entry ----------
if __name__ == "__main__":
    app.run()
