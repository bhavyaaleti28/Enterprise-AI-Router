def route_request(decision, classification):
    import json

    try:
        result = json.loads(classification)
    except json.JSONDecodeError:
        return {
            "status": "HUMAN_REVIEW",
            "message": "The classification could not be processed."
        }

    domain = result.get("domain")
    workflow = result.get("workflow")

    if decision == "UNRECOGNISED":
        return {
            "status": "UNRECOGNISED",
            "message": "The request does not match any enterprise workflow."
        }

    if decision == "HUMAN_REVIEW":
        return {
            "status": "HUMAN_REVIEW",
            "message": "The request requires human review.",
            "domain": domain
        }

    if decision == "ROUTE":
        return {
            "status": "ROUTE",
            "domain": domain,
            "workflow": workflow
        }

    return {
        "status": "HUMAN_REVIEW",
        "message": "Unknown routing decision."
    }