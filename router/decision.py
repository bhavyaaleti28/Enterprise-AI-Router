import csv
import json
from router.data_loader import load_workflows


WORKFLOW_DATA = load_workflows("data/domain_workflows.csv")


def load_keywords(file_path):
    keywords = {}

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            key = (row["domain"].strip(), row["workflow"].strip())

            keywords[key] = [
                keyword.strip().lower()
                for keyword in row["keywords"].split("|")
            ]

    return keywords


WORKFLOW_KEYWORDS = load_keywords("data/workflow_keywords.csv")


def has_workflow_evidence(request, domain, workflow):
    key = (domain, workflow)

    if key not in WORKFLOW_KEYWORDS:
        return False

    request = request.lower()

    for keyword in WORKFLOW_KEYWORDS[key]:
        if keyword in request:
            return True

    return False


def make_decision(classification, user_request):
    try:
        result = json.loads(classification)
    except json.JSONDecodeError:
        return "HUMAN_REVIEW"

    domain = result.get("domain")
    workflow = result.get("workflow")

    domain_confidence = result.get("domain_confidence", 0.0)
    workflow_confidence = result.get("workflow_confidence", 0.0)

    # No enterprise domain identified
    if domain is None:
        return "UNRECOGNISED"

    # Domain is not part of our closed set
    if domain not in WORKFLOW_DATA:
        return "UNRECOGNISED"

    # Enterprise domain identified but workflow is unclear
    if workflow is None:
        return "HUMAN_REVIEW"

    # Workflow is not part of the selected domain
    if workflow not in WORKFLOW_DATA[domain]:
        return "HUMAN_REVIEW"

    # Confidence check
    if domain_confidence < 0.7 or workflow_confidence < 0.7:
        return "HUMAN_REVIEW"

    # Evidence check
    if not has_workflow_evidence(user_request, domain, workflow):
        return "HUMAN_REVIEW"

    return "ROUTE"