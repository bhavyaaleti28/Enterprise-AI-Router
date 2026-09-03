import csv


def load_workflows(file_path):
    workflows = {}

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            domain = row["domain"].strip()
            workflow = row["workflow"].strip()

            if domain not in workflows:
                workflows[domain] = []

            workflows[domain].append(workflow)

    return workflows