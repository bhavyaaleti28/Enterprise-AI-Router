import json

from router.data_loader import load_workflows


WORKFLOW_DATA = load_workflows("data/domain_workflows.csv")

CONFIDENCE_THRESHOLD = 0.7


def make_decision(classification, user_request):
    try:
        result = json.loads(classification)
    except json.JSONDecodeError:
        return "HUMAN_REVIEW"

    domain = result.get("domain")
    workflow = result.get("workflow")

    domain_confidence = result.get("domain_confidence", 0.0)
    workflow_confidence = result.get("workflow_confidence", 0.0)

    if domain is None:
        return "UNRECOGNISED"

    if domain not in WORKFLOW_DATA:
        return "UNRECOGNISED"

    if workflow is None:
        return "HUMAN_REVIEW"

    if workflow not in WORKFLOW_DATA[domain]:
        return "HUMAN_REVIEW"

    if domain_confidence < CONFIDENCE_THRESHOLD:
        return "HUMAN_REVIEW"

    if workflow_confidence < CONFIDENCE_THRESHOLD:
        return "HUMAN_REVIEW"

    return "ROUTE"
