import sqlite3
from datetime import datetime

from router.data_loader import load_workflows


DATABASE_NAME = "requests.db"
WORKFLOW_DATA = load_workflows("data/domain_workflows.csv")

DEMO_ACCOUNTS = [
    ("employee", "employee123", "EMPLOYEE", "EMPLOYEE", "Employee"),
    ("hr_admin", "hr123", "HR", "DOMAIN_ADMIN", "HR Admin"),
    ("it_admin", "it123", "IT_SUPPORT", "DOMAIN_ADMIN", "IT Support Admin"),
    ("finance_admin", "finance123", "FINANCE", "DOMAIN_ADMIN", "Finance Admin"),
    ("facilities_admin", "facilities123", "FACILITIES", "DOMAIN_ADMIN", "Facilities Admin"),
    ("operations_admin", "operations123", "OPERATIONS", "DOMAIN_ADMIN", "Operations Admin"),
    ("legal_admin", "legal123", "LEGAL", "DOMAIN_ADMIN", "Legal Admin"),
    ("security_admin", "security123", "SECURITY", "DOMAIN_ADMIN", "Security Admin"),
    ("sales_admin", "sales123", "SALES", "DOMAIN_ADMIN", "Sales Admin"),
]

STATUS_ROUTED = "ROUTED"
STATUS_HUMAN_REVIEW = "HUMAN_REVIEW"
STATUS_WAITING = "WAITING_FOR_INFORMATION"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_COMPLETED = "COMPLETED"
STATUS_REJECTED = "REJECTED"
STATUS_UNRECOGNISED = "UNRECOGNISED"

STATUS_FILTERS = {
    "All": None,
    "Completed": STATUS_COMPLETED,
    "In Progress": STATUS_IN_PROGRESS,
    "Rejected": STATUS_REJECTED,
    "Waiting for Info": STATUS_WAITING,
}

REQUEST_COLUMNS = """
    id,
    request_text,
    domain,
    workflow,
    decision,
    created_at,
    review_status,
    reviewed_workflow,
    submitted_by,
    status,
    clarification_message,
    employee_response,
    rejection_reason,
    updated_at
"""


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _initial_status(decision):
    if decision == "ROUTE":
        return STATUS_ROUTED
    if decision == "HUMAN_REVIEW":
        return STATUS_HUMAN_REVIEW
    return STATUS_UNRECOGNISED


def _migrate_requests_table(cursor):
    cursor.execute("PRAGMA table_info(requests)")
    existing = {row[1] for row in cursor.fetchall()}

    new_columns = [
        ("submitted_by", "TEXT"),
        ("status", "TEXT"),
        ("clarification_message", "TEXT"),
        ("employee_response", "TEXT"),
        ("rejection_reason", "TEXT"),
        ("updated_at", "TEXT"),
    ]

    for name, col_type in new_columns:
        if name not in existing:
            cursor.execute(
                f"ALTER TABLE requests ADD COLUMN {name} {col_type}"
            )

    cursor.execute("""
        UPDATE requests
        SET status = 'HUMAN_REVIEW'
        WHERE status IS NULL
        AND decision = 'HUMAN_REVIEW'
        AND (review_status = 'PENDING' OR review_status IS NULL)
    """)
    cursor.execute("""
        UPDATE requests
        SET status = 'ROUTED'
        WHERE status IS NULL
        AND (decision = 'ROUTE' OR review_status = 'RESOLVED')
    """)
    cursor.execute("""
        UPDATE requests
        SET status = 'UNRECOGNISED'
        WHERE status IS NULL
        AND decision = 'UNRECOGNISED'
    """)
    cursor.execute("""
        UPDATE requests
        SET updated_at = created_at
        WHERE updated_at IS NULL
    """)


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
            reviewed_workflow TEXT,
            submitted_by TEXT,
            status TEXT,
            clarification_message TEXT,
            employee_response TEXT,
            rejection_reason TEXT,
            updated_at TEXT
        )
    """)

    _migrate_requests_table(cursor)
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


def seed_demo_accounts():
    for username, password, domain, role, _label in DEMO_ACCOUNTS:
        add_user(username, password, domain, role)


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
    submitted_by=None,
):
    connection = get_connection()
    cursor = connection.cursor()

    now = _now()
    status = _initial_status(decision)
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
            review_status,
            submitted_by,
            status,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        request_text,
        domain,
        workflow,
        decision,
        domain_confidence,
        workflow_confidence,
        now,
        review_status,
        submitted_by,
        status,
        now,
    ))

    connection.commit()
    connection.close()


def _fetch(query, params):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    connection.close()
    return rows


def get_all_requests_by_domain(domain, workflow_filter=None, status_filter=None):
    query = f"""
        SELECT {REQUEST_COLUMNS}
        FROM requests
        WHERE domain = ?
    """
    params = [domain]

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    if workflow_filter:
        query += " AND (workflow = ? OR reviewed_workflow = ?)"
        params.extend([workflow_filter, workflow_filter])

    query += " ORDER BY COALESCE(updated_at, created_at) DESC"
    return _fetch(query, params)


def get_requests_by_status(domain, status, workflow_filter=None):
    return get_all_requests_by_domain(domain, workflow_filter, status)


def get_requests_by_decision(domain, decision, workflow_filter=None):
    connection = get_connection()
    cursor = connection.cursor()

    query = f"""
        SELECT {REQUEST_COLUMNS}
        FROM requests
        WHERE domain = ?
        AND decision = ?
    """
    params = [domain, decision]

    if workflow_filter:
        query += " AND (workflow = ? OR reviewed_workflow = ?)"
        params.extend([workflow_filter, workflow_filter])

    query += " ORDER BY COALESCE(updated_at, created_at) DESC"
    cursor.execute(query, params)
    requests = cursor.fetchall()
    connection.close()
    return requests


def get_human_review_requests(domain):
    return _fetch(f"""
        SELECT {REQUEST_COLUMNS}
        FROM requests
        WHERE domain = ?
        AND status = '{STATUS_HUMAN_REVIEW}'
        AND review_status = 'PENDING'
        ORDER BY COALESCE(updated_at, created_at) DESC
    """, (domain,))


def get_requests_by_user(username, status_filter=None):
    query = f"""
        SELECT {REQUEST_COLUMNS}
        FROM requests
        WHERE submitted_by = ?
    """
    params = [username]

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY COALESCE(updated_at, created_at) DESC"
    return _fetch(query, params)


def get_request_counts(domain):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM requests WHERE domain = ?",
        (domain,),
    )
    total = cursor.fetchone()[0]

    def count_status(status):
        cursor.execute(
            "SELECT COUNT(*) FROM requests WHERE domain = ? AND status = ?",
            (domain, status),
        )
        return cursor.fetchone()[0]

    result = {
        "total": total,
        "routed": count_status(STATUS_ROUTED),
        "human_review": count_status(STATUS_HUMAN_REVIEW),
        "in_progress": count_status(STATUS_IN_PROGRESS),
        "completed": count_status(STATUS_COMPLETED),
        "rejected": count_status(STATUS_REJECTED),
        "waiting": count_status(STATUS_WAITING),
    }

    connection.close()
    return result


def resolve_human_review(request_id, workflow, admin_domain):
    if workflow not in WORKFLOW_DATA.get(admin_domain, []):
        return False

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE requests
        SET
            decision = 'ROUTE',
            status = ?,
            review_status = 'RESOLVED',
            reviewed_workflow = ?,
            workflow = ?,
            updated_at = ?
        WHERE id = ?
        AND domain = ?
        AND status = ?
        AND review_status = 'PENDING'
    """, (
        STATUS_ROUTED,
        workflow,
        workflow,
        _now(),
        request_id,
        admin_domain,
        STATUS_HUMAN_REVIEW,
    ))

    updated = cursor.rowcount > 0
    connection.commit()
    connection.close()
    return updated


def request_clarification(request_id, message, admin_domain):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE requests
        SET
            status = ?,
            clarification_message = ?,
            updated_at = ?
        WHERE id = ?
        AND domain = ?
        AND status = ?
        AND review_status = 'PENDING'
    """, (
        STATUS_WAITING,
        message.strip(),
        _now(),
        request_id,
        admin_domain,
        STATUS_HUMAN_REVIEW,
    ))

    updated = cursor.rowcount > 0
    connection.commit()
    connection.close()
    return updated


def submit_employee_response(request_id, response, username):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE requests
        SET
            status = ?,
            review_status = 'PENDING',
            employee_response = ?,
            updated_at = ?
        WHERE id = ?
        AND submitted_by = ?
        AND status = ?
    """, (
        STATUS_HUMAN_REVIEW,
        response.strip(),
        _now(),
        request_id,
        username,
        STATUS_WAITING,
    ))

    updated = cursor.rowcount > 0
    connection.commit()
    connection.close()
    return updated


def approve_request(request_id, admin_domain):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE requests
        SET status = ?, updated_at = ?
        WHERE id = ?
        AND domain = ?
        AND status = ?
    """, (STATUS_IN_PROGRESS, _now(), request_id, admin_domain, STATUS_ROUTED))

    updated = cursor.rowcount > 0
    connection.commit()
    connection.close()
    return updated


def reject_request(request_id, reason, admin_domain):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE requests
        SET
            status = ?,
            rejection_reason = ?,
            updated_at = ?
        WHERE id = ?
        AND domain = ?
        AND status = ?
    """, (
        STATUS_REJECTED,
        reason.strip(),
        _now(),
        request_id,
        admin_domain,
        STATUS_ROUTED,
    ))

    updated = cursor.rowcount > 0
    connection.commit()
    connection.close()
    return updated


def mark_completed(request_id, admin_domain):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE requests
        SET status = ?, updated_at = ?
        WHERE id = ?
        AND domain = ?
        AND status = ?
    """, (
        STATUS_COMPLETED,
        _now(),
        request_id,
        admin_domain,
        STATUS_IN_PROGRESS,
    ))

    updated = cursor.rowcount > 0
    connection.commit()
    connection.close()
    return updated
