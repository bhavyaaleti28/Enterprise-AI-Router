import csv
import json

from router.classifier import classify_request


def load_test_data(file_path):
    test_data = []

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            test_data.append(row)

    return test_data


def evaluate():
    test_data = load_test_data("data/test_requests.csv")

    total = len(test_data)
    correct_domains = 0
    correct_workflows = 0

    print("\n========== P18 EVALUATION ==========\n")

    for row in test_data:
        request = row["request"]
        expected_domain = row["expected_domain"]
        expected_workflow = row["expected_workflow"]

        classification = classify_request(request)

        try:
            result = json.loads(classification)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON: {request}")
            continue

        predicted_domain = result.get("domain")
        predicted_workflow = result.get("workflow")

        if expected_domain == "UNRECOGNISED":
            domain_correct = predicted_domain is None
        else:
            domain_correct = predicted_domain == expected_domain

        # Workflow is only checked when an expected workflow exists
        workflow_correct = True

        if expected_workflow:
            workflow_correct = predicted_workflow == expected_workflow

        if domain_correct:
            correct_domains += 1

        if workflow_correct and expected_workflow:
            correct_workflows += 1

        status = "✓" if domain_correct and workflow_correct else "✗"

        print(
            f"{status} {request}\n"
            f"   Expected: {expected_domain}"
            f"{' → ' + expected_workflow if expected_workflow else ''}\n"
            f"   Predicted: {predicted_domain}"
            f"{' → ' + str(predicted_workflow) if predicted_workflow else ''}\n"
        )

    enterprise_tests = sum(
        1 for row in test_data if row["expected_domain"] != "UNRECOGNISED"
    )

    workflow_tests = sum(
        1 for row in test_data if row["expected_workflow"]
    )

    domain_accuracy = (correct_domains / total) * 100 if total else 0
    workflow_accuracy = (
        (correct_workflows / workflow_tests) * 100
        if workflow_tests
        else 0
    )

    print("========== RESULTS ==========")
    print(f"Total test cases: {total}")
    print(f"Correct domains: {correct_domains}/{total}")
    print(f"Domain accuracy: {domain_accuracy:.2f}%")
    print()
    print(f"Workflow tests: {workflow_tests}")
    print(f"Correct workflows: {correct_workflows}/{workflow_tests}")
    print(f"Workflow accuracy: {workflow_accuracy:.2f}%")
    print("=============================\n")


if __name__ == "__main__":
    evaluate()
