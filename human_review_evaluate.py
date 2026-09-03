import csv
import json

from httpx import request

from router.classifier import classify_request
from router.decision import make_decision


def load_test_data(file_path):
    test_data = []

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            test_data.append(row)

    return test_data


def evaluate():
    test_data = load_test_data("data/human_review_tests.csv")

    correct = 0
    total = len(test_data)

    print("\n========== HUMAN REVIEW EVALUATION ==========\n")

    for row in test_data:
        request = row["request"]
        expected = row["expected_decision"]

        classification = classify_request(request)
        decision = make_decision(classification, request)

        if decision == expected:
            correct += 1
            symbol = "✓"
        else:
            symbol = "✗"

        print(f"{symbol} {request}")
        print(f"   Expected: {expected}")
        print(f"   Predicted: {decision}")

        try:
            result = json.loads(classification)
            print(
                f"   Domain: {result.get('domain')}"
                f" | Workflow: {result.get('workflow')}"
            )
        except json.JSONDecodeError:
            print("   Invalid classifier output")

        print()

    accuracy = (correct / total) * 100 if total else 0

    print("========== RESULTS ==========")
    print(f"Total test cases: {total}")
    print(f"Correct decisions: {correct}/{total}")
    print(f"Human-review accuracy: {accuracy:.2f}%")
    print("=============================\n")


if __name__ == "__main__":
    evaluate()