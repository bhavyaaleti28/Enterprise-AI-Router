import json
from router.ollama_client import ask_ollama
from router.data_loader import load_workflows


WORKFLOW_DATA = load_workflows("data/domain_workflows.csv")


def classify_request(user_request):
    prompt = f"""
You are an enterprise request classification system.

Classify the user's request using ONLY the enterprise domains and
workflows provided below.

AVAILABLE DOMAINS AND WORKFLOWS:

{json.dumps(WORKFLOW_DATA, indent=2)}

Return valid JSON in exactly this format:

{{
    "domain": "DOMAIN_NAME or null",
    "workflow": "WORKFLOW_NAME or null",
    "domain_confidence": 0.00,
    "workflow_confidence": 0.00
}}

Rules:

1. Select a domain ONLY from the available domains.
2. Select a workflow ONLY from the workflows belonging to the
   selected domain.
3. The workflow may be null.
4. If the request clearly belongs to an enterprise domain but
   there is not enough information to identify a specific workflow,
   return the correct domain and set workflow to null.
5. If the request does not belong to any available enterprise
   domain, set both domain and workflow to null.
6. domain_confidence must be between 0.0 and 1.0.
7. workflow_confidence must be between 0.0 and 1.0.
8. Domain confidence represents how confident you are about the
   selected enterprise domain.
9. Workflow confidence represents how confident you are about
   the specific workflow.
10. Do not invent domains or workflows.
11. Do not guess a specific workflow when the request is too vague.
12. Return ONLY valid JSON.
13. Do not include explanations or markdown.

Examples:

User: "I forgot my company password."

{{
    "domain": "IT_SUPPORT",
    "workflow": "password_reset",
    "domain_confidence": 1.0,
    "workflow_confidence": 1.0
}}

User: "I have an issue with my account."

{{
    "domain": "IT_SUPPORT",
    "workflow": null,
    "domain_confidence": 0.8,
    "workflow_confidence": 0.0
}}

User: "Tell me a joke."

{{
    "domain": null,
    "workflow": null,
    "domain_confidence": 0.0,
    "workflow_confidence": 0.0
}}

User request:
{user_request}
"""

    return ask_ollama(prompt).strip()