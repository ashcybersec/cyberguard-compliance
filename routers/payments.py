import os
import stripe
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from agents.evidence_agent import EvidencePackAgent
from services.doc_builder import EvidencePackBuilder
from stripe_service import create_checkout_session, retrieve_payload, delete_payload

router  = APIRouter(prefix="/api/v1", tags=["Payments"])
agent   = EvidencePackAgent()
builder = EvidencePackBuilder()

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://ceready.co.uk")

class CheckoutRequest:
    def __init__(self, payload: dict):
        self.payload = payload

from pydantic import BaseModel

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

@router.get("/download-pack")
async def download_pack(session_id: str, background: BackgroundTasks):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status != "paid":
            raise HTTPException(status_code=402, detail="Payment not completed.")

        payload = retrieve_payload(session_id)
        if not payload:
            raise HTTPException(status_code=404, detail="Session expired. Please contact support.")

        documents = agent.generate(payload)
        company   = payload.get("client", {}).get("company_name", "Organisation")
        zip_path  = builder.build_zip(company, documents)
        delete_payload(session_id)

        def cleanup():
            import os as _os
            if _os.path.exists(zip_path):
                _os.remove(zip_path)

        background.add_task(cleanup)

        return FileResponse(
            path=zip_path,
            media_type="application/zip",
            filename=f"CyberGuard_EvidencePack_{company.replace(' ', '_')}.zip",
            background=background,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
