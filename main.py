from router.classifier import classify_request
from router.decision import make_decision
from router.router import route_request


test_requests = [
    "I forgot my company password.",
    "I want to apply for leave.",
    "The AC in my office is broken.",
    "I have an issue with my account.",
    "I need help from HR.",
    "I have a problem at the office.",
    "Tell me a joke."
]


for request in test_requests:
    classification = classify_request(request)

    decision = make_decision(classification, request)

    routing = route_request(decision, classification)

    print("\nRequest:", request)
    print("Classification:", classification)
    print("Decision:", decision)
    print("Routing:", routing)