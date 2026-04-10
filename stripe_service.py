import os
import json
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

STORE_DIR = "/tmp/cyberguard_sessions"
os.makedirs(STORE_DIR, exist_ok=True)

def store_payload(session_id: str, payload: dict):
    path = os.path.join(STORE_DIR, f"{session_id}.json")
    with open(path, "w") as f:
        json.dump(payload, f)

def retrieve_payload(session_id: str) -> dict | None:
    path = os.path.join(STORE_DIR, f"{session_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def delete_payload(session_id: str):
    path = os.path.join(STORE_DIR, f"{session_id}.json")
    if os.path.exists(path):
        os.remove(path)

def create_checkout_session(payload: dict, success_url: str, cancel_url: str):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "gbp",
                "unit_amount": 4900,
                "product_data": {
                    "name": "CyberGuard Evidence Pack",
                    "description": "7 submission-ready Word policy documents aligned to NCSC Cyber Essentials v3.3.",
                },
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "product": "evidence_pack",
            "company_name": payload.get("client", {}).get("company_name", ""),
        },
    )
    store_payload(session.id, payload)
    return session.url, session.id
