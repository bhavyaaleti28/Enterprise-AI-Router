import json

import streamlit as st

from database.database import (
    authenticate_user,
    get_all_requests_by_domain,
    get_human_review_requests,
    get_request_counts,
    get_requests_by_decision,
    resolve_human_review,
    save_request,
)
from router.classifier import classify_request
from router.data_loader import load_workflows
from router.decision import make_decision
from router.router import route_request


WORKFLOWS = load_workflows("data/domain_workflows.csv")

DOMAIN_LABELS = {
    "HR": "HR",
    "IT_SUPPORT": "IT Support",
}


st.set_page_config(
    page_title="Enterprise AI Workflow Router",
    page_icon="🔀",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 18px;
        color: #9ca3af;
        margin-bottom: 30px;
    }
    .result-label {
        font-size: 16px;
        color: #9ca3af;
        margin-bottom: 4px;
    }
    .result-value {
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 20px;
    }
    .route-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #123c28;
        border: 1px solid #1f7a4d;
    }
    .review-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #454419;
        border: 1px solid #77731c;
    }
    .unrecognised-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #452326;
        border: 1px solid #783c42;
    }
    .decision-text {
        font-size: 22px;
        font-weight: 700;
        color: white;
    }
    .info-text {
        margin-top: 10px;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None


def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()


def render_header(title_suffix=None):
    st.markdown(
        '<div class="main-title">Enterprise AI Workflow Router</div>',
        unsafe_allow_html=True,
    )
    if title_suffix:
        st.markdown(
            f'<div class="subtitle">{title_suffix}</div>',
            unsafe_allow_html=True,
        )


def render_login_page():
    render_header("Login to access the workflow router.")
    st.markdown("### Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", type="primary"):
        user = authenticate_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid username or password.")


def display_request_card(row, show_review_actions=False, admin_domain=None):
    (
        request_id,
        request_text,
        domain,
        workflow,
        decision,
        created_at,
        review_status,
        reviewed_workflow,
    ) = row

    with st.container(border=True):
        st.markdown(f"**Request #{request_id}**")
        st.write(request_text)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Domain:** {domain}")
        with col2:
            st.write(f"**Workflow:** {workflow if workflow else '—'}")
        with col3:
            st.write(f"**Decision:** {decision}")

        st.caption(f"Created: {created_at}")

        if review_status == "RESOLVED" and reviewed_workflow:
            st.success(
                f"Resolved via human review → `{reviewed_workflow}`"
            )
        elif decision == "HUMAN_REVIEW" and review_status == "PENDING":
            st.warning("Pending human review")

        if show_review_actions and review_status == "PENDING":
            available = WORKFLOWS.get(admin_domain, [])
            if not available:
                st.error("No workflows configured for this domain.")
                return

            selected_workflow = st.selectbox(
                "Correct workflow",
                available,
                key=f"workflow_{request_id}",
            )

            if st.button(
                "Resolve & Route",
                key=f"resolve_{request_id}",
                type="primary",
            ):
                if resolve_human_review(
                    request_id,
                    selected_workflow,
                    admin_domain,
                ):
                    st.success(
                        f"Request routed to {selected_workflow}"
                    )
                    st.rerun()
                else:
                    st.error(
                        "Could not resolve this request. "
                        "It may have already been resolved."
                    )


def render_admin_dashboard(user_domain, username):
    label = DOMAIN_LABELS.get(user_domain, user_domain)
    render_header(f"{label} Dashboard")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.write(f"**User:** {username}")
    with col2:
        st.write(f"**Domain:** {user_domain}")
    with col3:
        if st.button("Logout"):
            logout()

    st.divider()

    total, routed, human_review = get_request_counts(user_domain)
    domain_workflows = WORKFLOWS.get(user_domain, [])

    tab_overview, tab_requests, tab_review = st.tabs(
        ["Overview", "All Requests", "Human Review"]
    )

    with tab_overview:
        st.markdown("### Dashboard Overview")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Requests", total)
        with c2:
            st.metric("Routed Requests", routed)
        with c3:
            st.metric("Human Review Requests", human_review)

        st.markdown("### Available Workflows")
        if domain_workflows:
            for wf in domain_workflows:
                st.write(f"- `{wf}`")
        else:
            st.info("No workflows configured for this domain.")

    with tab_requests:
        st.markdown("### Requests")

        filter_col, workflow_col = st.columns(2)
        with filter_col:
            decision_filter = st.selectbox(
                "Filter by decision",
                ["All", "ROUTE", "HUMAN_REVIEW"],
                key="decision_filter",
            )
        with workflow_col:
            workflow_options = ["All"] + domain_workflows
            workflow_filter = st.selectbox(
                "Filter by workflow",
                workflow_options,
                key="workflow_filter",
            )

        wf = None if workflow_filter == "All" else workflow_filter

        if decision_filter == "All":
            requests = get_all_requests_by_domain(user_domain, wf)
        else:
            requests = get_requests_by_decision(
                user_domain,
                decision_filter,
                wf,
            )

        if not requests:
            st.info("No requests found.")
        else:
            for row in requests:
                display_request_card(row)

    with tab_review:
        st.markdown("### Pending Human Review")
        pending = get_human_review_requests(user_domain)

        if not pending:
            st.info("No pending human review requests.")
        else:
            for row in pending:
                display_request_card(
                    row,
                    show_review_actions=True,
                    admin_domain=user_domain,
                )


def render_employee_page(username):
    render_header(
        "Classify an enterprise request and route it to the appropriate workflow."
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**User:** {username}")
    with col2:
        if st.button("Logout"):
            logout()

    st.divider()

    example = st.selectbox(
        "Try an example",
        [
            "Choose an example...",
            "I forgot my company password.",
            "I want to apply for leave.",
            "The AC in my office is broken.",
            "I need help from HR.",
            "Tell me a joke.",
        ],
    )

    request = st.text_area(
        "Enter your request",
        value="" if example == "Choose an example..." else example,
        placeholder="Example: I forgot my company password.",
        height=120,
    )

    if st.button("Classify Request", type="primary"):
        if not request.strip():
            st.warning("Please enter a request.")
        else:
            with st.spinner("Classifying request..."):
                classification = classify_request(request)
                decision = make_decision(classification, request)
                route_request(decision, classification)

            try:
                result = json.loads(classification)
                domain = result.get("domain")
                workflow = result.get("workflow")
                domain_confidence = result.get("domain_confidence")
                workflow_confidence = result.get("workflow_confidence")
            except json.JSONDecodeError:
                domain = None
                workflow = None
                domain_confidence = None
                workflow_confidence = None

            save_request(
                request_text=request,
                domain=domain,
                workflow=workflow,
                decision=decision,
                domain_confidence=domain_confidence,
                workflow_confidence=workflow_confidence,
            )

            st.divider()

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    '<div class="result-label">Domain</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="result-value">'
                    f'{domain if domain else "—"}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    '<div class="result-label">Workflow</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="result-value">'
                    f'{workflow if workflow else "—"}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("### Decision")

            if decision == "ROUTE":
                st.markdown(
                    """
                    <div class="route-box">
                        <div class="decision-text">✓ ROUTE</div>
                        <div class="info-text">
                            Request can be safely routed to the selected workflow.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Routing:** `{domain} → {workflow}`")

            elif decision == "HUMAN_REVIEW":
                st.markdown(
                    """
                    <div class="review-box">
                        <div class="decision-text">⚠ HUMAN REVIEW</div>
                        <div class="info-text">
                            The request belongs to an enterprise area, but the
                            specific workflow is not clear enough for automatic
                            routing.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if domain:
                    st.markdown(f"**Detected domain:** `{domain}`")

            elif decision == "UNRECOGNISED":
                st.markdown(
                    """
                    <div class="unrecognised-box">
                        <div class="decision-text">✕ UNRECOGNISED</div>
                        <div class="info-text">
                            This request does not match any enterprise workflow.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.divider()
    st.caption(
        "Enterprise AI Workflow Router • Powered by Ollama and Llama 3:8B"
    )


def main():
    init_session_state()

    if not st.session_state.logged_in:
        render_login_page()
        st.stop()

    user = st.session_state.user
    username = user[1]
    user_domain = user[2]
    user_role = user[3]

    if user_role == "DOMAIN_ADMIN":
        render_admin_dashboard(user_domain, username)
    else:
        render_employee_page(username)


if __name__ == "__main__":
    main()
