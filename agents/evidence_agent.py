import json
import os
import anthropic
from dotenv import load_dotenv
from prompts.evidence_pack import EVIDENCE_PACK_SYSTEM_PROMPT, build_evidence_prompt

load_dotenv()

DOCUMENT_KEYS = [
    "scope_statement",
    "information_security_policy",
    "access_control_policy",
    "patch_management_policy",
    "firewall_network_policy",
    "malware_protection_policy",
    "asset_register_guidance",
]

class EvidencePackAgent:
    MODEL      = "claude-haiku-4-5"
    MAX_TOKENS = 4096

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(self, assessment_data: dict) -> dict:
        """Generate each document in a separate API call and combine."""
        documents = {}
        base_prompt = build_evidence_prompt(assessment_data)

        for doc_key in DOCUMENT_KEYS:
            prompt = (
                f"{base_prompt}\n\n"
                f"Generate ONLY the '{doc_key}' document now.\n"
                f"Return ONLY a JSON object with a single key '{doc_key}' "
                f"containing the full document text as a string."
            )
            try:
                message = self.client.messages.create(
                    model      = self.MODEL,
                    max_tokens = self.MAX_TOKENS,
                    system     = EVIDENCE_PACK_SYSTEM_PROMPT,
                    messages   = [{"role": "user", "content": prompt}]
                )
                raw = message.content[0].text.strip()
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                    raw = raw.strip()

                result = json.loads(raw)
                documents[doc_key] = result.get(doc_key, "")

            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON for {doc_key}: {e}")
            except anthropic.APIError as e:
                raise RuntimeError(f"Claude API error on {doc_key}: {e}")

        return documents
