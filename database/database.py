import sqlite3
from datetime import datetime

from router.data_loader import load_workflows


DATABASE_NAME = "requests.db"
WORKFLOW_DATA = load_workflows("data/domain_workflows.csv")


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            domain TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_text TEXT NOT NULL,
            domain TEXT,
            workflow TEXT,
            decision TEXT NOT NULL,
            domain_confidence REAL,
            workflow_confidence REAL,
            created_at TEXT NOT NULL,
            review_status TEXT,
            reviewed_workflow TEXT
        )
    """)

    connection.commit()
    connection.close()


def add_user(username, password, domain, role):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (username, password, domain, role)
        VALUES (?, ?, ?, ?)
    """, (username, password, domain, role))

    connection.commit()
    connection.close()


def authenticate_user(username, password):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, username, domain, role
        FROM users
        WHERE username = ? AND password = ?
    """, (username, password))

    user = cursor.fetchone()
    connection.close()

    return user


def save_request(
    request_text,
    domain,
    workflow,
    decision,
    domain_confidence=None,
    workflow_confidence=None,
):
    connection = get_connection()
    cursor = connection.cursor()

    review_status = "PENDING" if decision == "HUMAN_REVIEW" else None

    cursor.execute("""
        INSERT INTO requests (
            request_text,
            domain,
            workflow,
            decision,
            domain_confidence,
            workflow_confidence,
            created_at,
            review_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        request_text,
        domain,
        workflow,
        decision,
        domain_confidence,
        workflow_confidence,
        datetime.now().isoformat(timespec="seconds"),
        review_status,
    ))

    connection.commit()
    connection.close()


def _request_columns():
    return """
        id,
        request_text,
        domain,
        workflow,
        decision,
        created_at,
        review_status,
        reviewed_workflow
    """


def get_all_requests_by_domain(domain, workflow_filter=None):
    connection = get_connection()
    cursor = connection.cursor()

    query = f"""
        SELECT {_request_columns()}
        FROM requests
        WHERE domain = ?
    """
    params = [domain]

    if workflow_filter:
        query += " AND (workflow = ? OR reviewed_workflow = ?)"
        params.extend([workflow_filter, workflow_filter])

    query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    requests = cursor.fetchall()
    connection.close()

    return requests


def get_requests_by_decision(domain, decision, workflow_filter=None):
    connection = get_connection()
    cursor = connection.cursor()

    query = f"""
        SELECT {_request_columns()}
        FROM requests
        WHERE domain = ?
        AND decision = ?
    """
    params = [domain, decision]

    if workflow_filter:
        query += " AND (workflow = ? OR reviewed_workflow = ?)"
        params.extend([workflow_filter, workflow_filter])

    query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    requests = cursor.fetchall()
    connection.close()

    return requests


def get_human_review_requests(domain):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(f"""
        SELECT {_request_columns()}
        FROM requests
        WHERE domain = ?
        AND decision = 'HUMAN_REVIEW'
        AND review_status = 'PENDING'
        ORDER BY created_at DESC
    """, (domain,))

    requests = cursor.fetchall()
    connection.close()

    return requests


def get_request_counts(domain):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM requests WHERE domain = ?",
        (domain,),
    )
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM requests
        WHERE domain = ?
        AND decision = 'ROUTE'
    """, (domain,))
    routed = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM requests
        WHERE domain = ?
        AND decision = 'HUMAN_REVIEW'
        AND review_status = 'PENDING'
    """, (domain,))
    human_review = cursor.fetchone()[0]

    connection.close()

    return total, routed, human_review


def resolve_human_review(request_id, workflow, admin_domain):
    if workflow not in WORKFLOW_DATA.get(admin_domain, []):
        return False

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE requests
        SET
            decision = 'ROUTE',
            review_status = 'RESOLVED',
            reviewed_workflow = ?,
            workflow = ?
        WHERE id = ?
        AND domain = ?
        AND decision = 'HUMAN_REVIEW'
        AND review_status = 'PENDING'
    """, (workflow, workflow, request_id, admin_domain))

    updated = cursor.rowcount > 0
    connection.commit()
    connection.close()

    return updated
