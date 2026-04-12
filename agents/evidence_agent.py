import json
import os
import anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    MAX_TOKENS = 8096

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
        self.client = anthropic.Anthropic(api_key=api_key)

    def _generate_single(self, doc_key: str, base_prompt: str) -> tuple[str, str]:
        """Generate a single document. Returns (doc_key, content)."""
        prompt = (
            f"{base_prompt}\n\n"
            f"Generate ONLY the '{doc_key}' document now.\n"
            f"Return ONLY a JSON object with a single key '{doc_key}' "
            f"containing the full document text as a string value. "
            f"Use real newline characters in the string, not \\\\n escape sequences."
        )
        try:
            message = self.client.messages.create(
                model      = self.MODEL,
                max_tokens = self.MAX_TOKENS,
                system     = EVIDENCE_PACK_SYSTEM_PROMPT,
                messages   = [{"role": "user", "content": prompt}]
            )
            raw = message.content[0].text.strip()

            # Strip markdown fences
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            result = json.loads(raw)
            return doc_key, result.get(doc_key, "")

        except json.JSONDecodeError:
            try:
                start = raw.index('{')
                end   = raw.rindex('}') + 1
                result = json.loads(raw[start:end])
                return doc_key, result.get(doc_key, raw[start:end])
            except Exception:
                return doc_key, raw
        except anthropic.APIError as e:
            raise RuntimeError(f"Claude API error on {doc_key}: {e}")

    def generate(self, assessment_data: dict) -> dict:
        """Generate all 7 documents in parallel. ~3x faster than sequential."""
        base_prompt = build_evidence_prompt(assessment_data)
        documents   = {}

        # Run all 7 API calls concurrently
        with ThreadPoolExecutor(max_workers=7) as executor:
            futures = {
                executor.submit(self._generate_single, doc_key, base_prompt): doc_key
                for doc_key in DOCUMENT_KEYS
            }
            for future in as_completed(futures):
                doc_key = futures[future]
                try:
                    key, content = future.result()
                    documents[key] = content
                except Exception as e:
                    print(f"[EVIDENCE] Error generating {doc_key}: {e}")
                    documents[doc_key] = f"Error generating {doc_key}: {e}"

        # Return in correct order
        return {k: documents.get(k, "") for k in DOCUMENT_KEYS}
