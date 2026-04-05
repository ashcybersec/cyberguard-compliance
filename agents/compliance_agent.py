from dotenv import load_dotenv
load_dotenv()
import json
import os
import anthropic
from models.questionnaire import AssessmentRequest, AssessmentResult, ControlResult, ControlGap, RiskLevel
from prompts.cyber_essentials import CYBER_ESSENTIALS_SYSTEM_PROMPT, build_assessment_prompt


class ComplianceAgent:
    """
    AI-powered Cyber Essentials compliance agent.
    Uses Claude Haiku for cost-efficient, high-quality gap analysis.
    """

    MODEL    = "claude-haiku-4-5"
    MAX_TOKENS = 8096


    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
        self.client = anthropic.Anthropic(api_key=api_key)

    def analyse(self, request: AssessmentRequest) -> AssessmentResult:
        """
        Run the full compliance gap analysis against the 5 Cyber Essentials controls.
        Returns a structured AssessmentResult.
        """
        request_dict = request.model_dump()
        user_prompt  = build_assessment_prompt(request_dict)

        try:
            message = self.client.messages.create(
                model      = self.MODEL,
                max_tokens = self.MAX_TOKENS,
                system     = CYBER_ESSENTIALS_SYSTEM_PROMPT,
                messages   = [{"role": "user", "content": user_prompt}]
            )

            raw_text = message.content[0].text.strip()

            # Strip markdown fences if model wraps in them
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()

            analysis = json.loads(raw_text)

        except json.JSONDecodeError as e:
            raise ValueError(f"AI agent returned invalid JSON: {e}")
        except anthropic.APIError as e:
            raise RuntimeError(f"Claude API error: {e}")

        return self._build_result(request.client, analysis)

    def _build_result(self, client_info, analysis: dict) -> AssessmentResult:
        """Map the raw JSON analysis into a typed AssessmentResult."""

        controls = []
        for ctrl in analysis.get("controls", []):
            gaps = [
                ControlGap(
                    gap_title         = g["gap_title"],
                    description       = g["description"],
                    remediation_steps = g["remediation_steps"],
                    priority          = g["priority"],
                    ncsc_reference    = g.get("ncsc_reference")
                )
                for g in ctrl.get("gaps", [])
            ]
            controls.append(
                ControlResult(
                    control_name  = ctrl["control_name"],
                    score         = ctrl["score"],
                    risk_level    = RiskLevel(ctrl["risk_level"]),
                    passed_checks = ctrl["passed_checks"],
                    total_checks  = ctrl["total_checks"],
                    gaps          = gaps,
                    summary       = ctrl["summary"]
                )
            )

        return AssessmentResult(
            client                  = client_info,
            overall_score           = analysis["overall_score"],
            overall_risk            = RiskLevel(analysis["overall_risk"]),
            cyber_essentials_ready  = analysis["cyber_essentials_ready"],
            controls                = controls,
            executive_summary       = analysis["executive_summary"],
            top_priorities          = analysis["top_priorities"],
            estimated_effort        = analysis["estimated_effort"]
        )
