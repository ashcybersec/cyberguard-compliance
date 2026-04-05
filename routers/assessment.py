import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from models.questionnaire import AssessmentRequest, AssessmentResult
from agents.compliance_agent import ComplianceAgent
from services.report_generator import ReportGenerator

router  = APIRouter(prefix="/api/v1", tags=["Assessment"])
agent   = ComplianceAgent()
reporter = ReportGenerator()


@router.post("/assess", response_model=AssessmentResult, summary="Run Cyber Essentials gap analysis")
async def run_assessment(request: AssessmentRequest):
    """
    Submit a completed Cyber Essentials questionnaire and receive a full
    AI-powered gap analysis with risk scores and remediation steps.
    """
    try:
        result = agent.analyse(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/assess/report", summary="Run assessment and return PDF report")
async def run_assessment_with_report(request: AssessmentRequest, background: BackgroundTasks):
    """
    Submit a questionnaire, receive gap analysis, and get a downloadable
    branded PDF report.
    """
    try:
        result   = agent.analyse(request)
        pdf_path = reporter.generate(result)

        def cleanup():
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

        background.add_task(cleanup)

        return FileResponse(
            path         = pdf_path,
            media_type   = "application/pdf",
            filename     = f"cyberguard_report_{request.client.company_name.replace(' ', '_')}.pdf",
            background   = background,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/health", summary="Health check")
async def health():
    return {"status": "ok", "service": "CyberGuard Compliance API"}
