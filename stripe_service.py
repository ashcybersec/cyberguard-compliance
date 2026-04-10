import os
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

_payload_store: dict = {}

def store_payload(session_id: str, payload: dict):
    _payload_store[session_id] = payload

def retrieve_payload(session_id: str) -> dict | None:
    return _payload_store.get(session_id)

def delete_payload(session_id: str):
    _payload_store.pop(session_id, None)

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
