import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from models.questionnaire import AssessmentRequest
from agents.evidence_agent import EvidencePackAgent
from services.doc_builder import EvidencePackBuilder

router  = APIRouter(prefix="/api/v1", tags=["Evidence Pack"])
agent   = EvidencePackAgent()
builder = EvidencePackBuilder()


@router.post("/evidence-pack", summary="Generate Cyber Essentials evidence pack (ZIP of Word docs)")
async def generate_evidence_pack(
    request: AssessmentRequest,
    background: BackgroundTasks
):
    """
    Submit a completed Cyber Essentials questionnaire and receive a ZIP file
    containing 7 fully branded, submission-ready policy documents:

    1. Scope Statement
    2. Information Security Policy
    3. Access Control Policy
    4. Patch Management Policy
    5. Firewall & Network Security Policy
    6. Malware Protection Policy
    7. Asset Register Guidance & Template

    All documents are pre-filled with the organisation's details and tailored
    to their specific gap findings. Aligned to NCSC Cyber Essentials v3.3.
    """
    try:
        payload   = request.model_dump()
        documents = agent.generate(payload)
        zip_path  = builder.build_zip(request.client.company_name, documents)

        def cleanup():
            if os.path.exists(zip_path):
                os.remove(zip_path)

        background.add_task(cleanup)

        safe_name = request.client.company_name.replace(" ", "_")

        return FileResponse(
            path       = zip_path,
            media_type = "application/zip",
            filename   = f"CyberGuard_EvidencePack_{safe_name}.zip",
            background = background,
        )

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
