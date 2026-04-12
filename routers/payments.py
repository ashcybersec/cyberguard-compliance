import os
import stripe
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from agents.evidence_agent import EvidencePackAgent
from services.doc_builder import EvidencePackBuilder
from services.email_service import send_evidence_pack_email, send_payment_receipt_email
from stripe_service import create_checkout_session, retrieve_payload, delete_payload

router  = APIRouter(prefix="/api/v1", tags=["Payments"])
agent   = EvidencePackAgent()
builder = EvidencePackBuilder()

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://cyberguard-frontend-production-e3cd.up.railway.app")

class CheckoutBody(BaseModel):
    payload: dict

@router.post("/checkout")
async def create_checkout(body: CheckoutBody):
    try:
        checkout_url, session_id = create_checkout_session(
            payload=body.payload,
            success_url=f"{FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}",
        )
        return {"checkout_url": checkout_url, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_and_email(payload: dict, session_id: str):
    """Background task — generate docs and email to customer."""
    import os as _os
    try:
        documents = agent.generate(payload)
        company   = payload.get("client", {}).get("company_name", "Organisation")
        email     = payload.get("client", {}).get("contact_email", "")
        zip_path  = builder.build_zip(company, documents)

        if email:
            send_evidence_pack_email(email, company, zip_path)
            send_payment_receipt_email(email, company)

        if _os.path.exists(zip_path):
            _os.remove(zip_path)

    except Exception as e:
        print(f"Background generation error: {e}")
    finally:
        delete_payload(session_id)

@router.get("/download-pack")
async def download_pack(session_id: str, background: BackgroundTasks):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status != "paid":
            raise HTTPException(status_code=402, detail="Payment not completed.")

        payload = retrieve_payload(session_id)
        if not payload:
            raise HTTPException(status_code=404, detail="Session expired. Please contact support at hello@ceready.co.uk")

        email   = payload.get("client", {}).get("contact_email", "")
        company = payload.get("client", {}).get("company_name", "Organisation")

        # Trigger background generation + email
        background.add_task(generate_and_email, payload, session_id)

        # Return immediately
        return JSONResponse(content={
            "status": "processing",
            "message": f"Your Evidence Pack is being prepared and will be emailed to {email} within 5 minutes.",
            "email": email,
            "company": company,
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
