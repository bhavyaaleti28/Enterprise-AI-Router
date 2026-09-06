import json

import streamlit as st

from database.database import (
    DEMO_ACCOUNTS,
    STATUS_FILTERS,
    approve_request,
    authenticate_user,
    get_all_requests_by_domain,
    get_human_review_requests,
    get_request_counts,
    get_requests_by_user,
    mark_completed,
    reject_request,
    request_clarification,
    resolve_human_review,
    save_request,
    submit_employee_response,
)
from router.classifier import classify_request
from router.data_loader import load_workflows
from router.decision import make_decision
from router.router import route_request
from ui.components import (
    render_classification_fields,
    render_decision_result,
    render_demo_accounts,
    render_empty_state,
    render_hero_banner,
    render_login_branding,
    render_metric_cards,
    render_request_card_html,
    render_sidebar_brand,
    render_user_toolbar,
    render_workflow_pills,
)
from ui.theme import get_domain_theme, inject_global_css


WORKFLOWS = load_workflows("data/domain_workflows.csv")

EXAMPLE_REQUESTS = [
    "Choose an example...",
    "I forgot my company password.",
    "I want to apply for leave.",
]


def init_session_state():
    defaults = {
        "logged_in": False,
        "user": None,
        "admin_page": "Overview",
        "employee_page": "Submit Request",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.admin_page = "Overview"
    st.session_state.employee_page = "Submit Request"
    st.rerun()


def render_login_page():
    inject_global_css()
    col_l, col_c, col_r = st.columns([0.5, 3, 0.5])
    with col_c:
        with st.container(border=True):
            render_login_branding()

            username = st.text_input("Username", placeholder="employee")
            password = st.text_input(
                "Password",
                type="password",
                placeholder="••••••••",
            )

            if st.button("Sign In", type="primary", use_container_width=True):
                user = authenticate_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

            with st.expander("Demo accounts", expanded=False):
                render_demo_accounts(DEMO_ACCOUNTS)


def render_human_review_actions(row, admin_domain):
    request_id = row[0]
    suggested_workflow = row[3]
    status = row[9]
    review_status = row[6]
    employee_response = row[12]

    if status != "HUMAN_REVIEW" or review_status != "PENDING":
        return

    available = WORKFLOWS.get(admin_domain, [])
    if not available:
        st.error("No workflows configured for this domain.")
        return

    default_index = 0
    if suggested_workflow and suggested_workflow in available:
        default_index = available.index(suggested_workflow)

    with st.container(border=True):
        st.markdown("**Human review actions**")
        if employee_response:
            st.info(f"Employee provided additional info: _{employee_response}_")

        selected = st.selectbox(
            "Select correct workflow",
            available,
            index=default_index,
            format_func=lambda x: x.replace("_", " ").title(),
            key=f"resolve_wf_{request_id}",
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "Resolve & Route",
                key=f"resolve_btn_{request_id}",
                type="primary",
                use_container_width=True,
            ):
                if resolve_human_review(request_id, selected, admin_domain):
                    st.success(
                        f"Request #{request_id} routed to "
                        f"**{selected.replace('_', ' ').title()}**"
                    )
                    st.rerun()
                else:
                    st.error("Could not resolve this request.")

        with col2:
            if st.button(
                "Request Clarification",
                key=f"clarify_toggle_{request_id}",
                use_container_width=True,
            ):
                st.session_state[f"show_clarify_{request_id}"] = True

        if st.session_state.get(f"show_clarify_{request_id}"):
            clarify_msg = st.text_area(
                "Message to employee",
                placeholder="Please provide more details about...",
                key=f"clarify_msg_{request_id}",
            )
            if st.button(
                "Send Clarification Request",
                key=f"clarify_send_{request_id}",
                use_container_width=True,
            ):
                if not clarify_msg.strip():
                    st.warning("Please enter a clarification message.")
                elif request_clarification(
                    request_id, clarify_msg, admin_domain
                ):
                    st.success("Clarification request sent to employee.")
                    st.session_state[f"show_clarify_{request_id}"] = False
                    st.rerun()
                else:
                    st.error("Could not send clarification request.")


def render_lifecycle_actions(row, admin_domain):
    request_id = row[0]
    status = row[9]

    if status == "ROUTED":
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "Approve",
                key=f"approve_{request_id}",
                type="primary",
                use_container_width=True,
            ):
                if approve_request(request_id, admin_domain):
                    st.success("Request approved — now In Progress.")
                    st.rerun()
                else:
                    st.error("Could not approve this request.")

        with col2:
            if st.button(
                "Reject",
                key=f"reject_toggle_{request_id}",
                use_container_width=True,
            ):
                st.session_state[f"show_reject_{request_id}"] = True

        if st.session_state.get(f"show_reject_{request_id}"):
            reason = st.text_area(
                "Rejection reason",
                key=f"reject_reason_{request_id}",
            )
            if st.button(
                "Confirm Reject",
                key=f"reject_confirm_{request_id}",
                use_container_width=True,
            ):
                if not reason.strip():
                    st.warning("Please provide a rejection reason.")
                elif reject_request(request_id, reason, admin_domain):
                    st.success("Request rejected.")
                    st.session_state[f"show_reject_{request_id}"] = False
                    st.rerun()
                else:
                    st.error("Could not reject this request.")

    elif status == "IN_PROGRESS":
        if st.button(
            "Mark Completed",
            key=f"complete_{request_id}",
            type="primary",
            use_container_width=True,
        ):
            if mark_completed(request_id, admin_domain):
                st.success("Request marked as completed.")
                st.rerun()
            else:
                st.error("Could not complete this request.")


def render_admin_request_actions(row, admin_domain, review_mode=False):
    status = row[9]
    review_status = row[6]

    is_pending_review = (
        status == "HUMAN_REVIEW" and review_status == "PENDING"
    )
    if review_mode or is_pending_review:
        render_human_review_actions(row, admin_domain)

    if status in ("ROUTED", "IN_PROGRESS"):
        render_lifecycle_actions(row, admin_domain)


def render_requests_list(requests, admin_domain=None, review_mode=False):
    if not requests:
        if review_mode:
            render_empty_state(
                "✅",
                "Queue is clear",
                "No requests are waiting for human review.",
            )
        else:
            render_empty_state(
                "📭",
                "No requests found",
                "Try adjusting your filters or wait for new submissions.",
            )
        return

    for row in requests:
        render_request_card_html(row)
        if admin_domain:
            render_admin_request_actions(row, admin_domain, review_mode)


def render_request_filters(key_prefix="admin"):
    """Status filter bar. Returns (status_label, status_value)."""
    session_key = f"status_filter_{key_prefix}"
    filter_options = list(STATUS_FILTERS.keys())
    default = st.session_state.get(session_key, "All")
    if default not in filter_options:
        default = "All"

    status_label = st.selectbox(
        "Filter by status",
        filter_options,
        index=filter_options.index(default),
        key=f"status_select_{key_prefix}",
    )
    st.session_state[session_key] = status_label
    return status_label, STATUS_FILTERS[status_label]


def render_admin_dashboard(user_domain, username):
    theme = get_domain_theme(user_domain)
    inject_global_css(theme["accent"], theme["accent_light"])

    counts = get_request_counts(user_domain)

    with st.sidebar:
        render_sidebar_brand(user_domain, username)

        nav_options = ["Overview", "All Requests", "Human Review"]
        page = st.radio(
            "Navigation",
            nav_options,
            index=nav_options.index(st.session_state.admin_page),
            label_visibility="collapsed",
        )
        st.session_state.admin_page = page

        if counts["human_review"] > 0:
            st.markdown(f"⚠ **{counts['human_review']}** pending review")
        if counts["waiting"] > 0:
            st.markdown(f"💬 **{counts['waiting']}** awaiting employee info")

        st.divider()
        if st.button("Logout", key="sidebar_logout", use_container_width=True):
            logout()

    domain_workflows = WORKFLOWS.get(user_domain, [])

    if render_user_toolbar(username, user_domain, "DOMAIN_ADMIN"):
        logout()

    render_hero_banner(user_domain)

    status_label, status_value = render_request_filters(
        key_prefix=st.session_state.admin_page
    )

    requests = get_all_requests_by_domain(user_domain, status_filter=status_value)

    if st.session_state.admin_page == "Overview":
        render_metric_cards(counts)

        st.markdown(
            '<p class="section-title">Available Workflows</p>',
            unsafe_allow_html=True,
        )
        render_workflow_pills(domain_workflows, user_domain)

        st.markdown(
            '<p class="section-title">Recent Activity</p>',
            unsafe_allow_html=True,
        )
        render_requests_list(
            requests[:5], admin_domain=user_domain
        )

    elif st.session_state.admin_page == "All Requests":
        st.markdown(
            f'<p class="section-title">'
            f'{len(requests)} Request{"s" if len(requests) != 1 else ""}'
            f' · {status_label}'
            f'</p>',
            unsafe_allow_html=True,
        )
        render_requests_list(requests, admin_domain=user_domain)

    elif st.session_state.admin_page == "Human Review":
        st.markdown(
            '<p class="section-title">Human Review Queue</p>',
            unsafe_allow_html=True,
        )
        if counts["human_review"] > 0 and status_label == "All":
            st.info(
                f"**{counts['human_review']}** request(s) need review. "
                "Resolve & route, or request clarification from the employee."
            )
        review_requests = (
            get_human_review_requests(user_domain)
            if status_label == "All"
            else [r for r in requests if r[9] == "HUMAN_REVIEW"]
        )
        render_requests_list(
            review_requests,
            admin_domain=user_domain,
            review_mode=True,
        )


def render_submit_request(username):
    st.markdown(
        """
        <div class="hero-banner" style="margin-bottom:0.5rem;">
            <div class="hero-badge">Employee Portal</div>
            <div class="hero-icon">📝</div>
            <h1 class="hero-title">Submit a Request</h1>
            <p class="hero-tagline">
                Describe your issue in plain language — the AI router will
                classify and route it to the right workflow.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="section-title">Your Request</p>',
        unsafe_allow_html=True,
    )

    example = st.selectbox(
        "Quick examples",
        EXAMPLE_REQUESTS,
        label_visibility="collapsed",
    )

    request = st.text_area(
        "Request text",
        value="" if example == EXAMPLE_REQUESTS[0] else example,
        placeholder="Example: I forgot my company password.",
        height=140,
        label_visibility="collapsed",
    )

    if st.button(
        "Classify & Route Request",
        type="primary",
        use_container_width=True,
    ):
        if not request.strip():
            st.warning("Please enter a request before classifying.")
        else:
            with st.spinner("Analysing your request with Llama 3..."):
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
                domain = workflow = None
                domain_confidence = workflow_confidence = None

            save_request(
                request_text=request,
                domain=domain,
                workflow=workflow,
                decision=decision,
                domain_confidence=domain_confidence,
                workflow_confidence=workflow_confidence,
                submitted_by=username,
            )

            st.markdown("---")
            st.markdown(
                '<p class="section-title">Classification Result</p>',
                unsafe_allow_html=True,
            )
            render_classification_fields(domain, workflow)
            render_decision_result(decision, domain, workflow)


def render_my_requests(username):
    status_label, status_value = render_request_filters(key_prefix="employee")

    st.markdown(
        f'<p class="section-title">My Requests · {status_label}</p>',
        unsafe_allow_html=True,
    )

    requests = get_requests_by_user(username, status_value)

    if not requests:
        render_empty_state(
            "📭",
            "No requests yet",
            "Submit a request to see it tracked here.",
        )
        return

    for row in requests:
        render_request_card_html(row)
        request_id = row[0]
        status = row[9]
        clarification_message = row[10]

        if status == "WAITING_FOR_INFORMATION" and clarification_message:
            with st.container(border=True):
                st.warning(f"**Clarification needed:** {clarification_message}")
                response = st.text_area(
                    "Your response",
                    placeholder="Provide the requested information...",
                    key=f"emp_response_{request_id}",
                )
                if st.button(
                    "Submit Information",
                    key=f"emp_submit_{request_id}",
                    type="primary",
                    use_container_width=True,
                ):
                    if not response.strip():
                        st.warning("Please enter your response.")
                    elif submit_employee_response(
                        request_id, response, username
                    ):
                        st.success(
                            "Information submitted. "
                            "Your request is back with the admin for review."
                        )
                        st.rerun()
                    else:
                        st.error("Could not submit your response.")


def render_employee_page(username):
    inject_global_css("#6366f1", "#eef2ff")

    if render_user_toolbar(username, role="EMPLOYEE"):
        logout()

    tab_submit, tab_my = st.tabs(["Submit Request", "My Requests"])

    with tab_submit:
        render_submit_request(username)

    with tab_my:
        render_my_requests(username)

    st.divider()
    st.caption(
        "Enterprise AI Workflow Router · Powered by Ollama & Llama 3:8B"
    )


def main():
    st.set_page_config(
        page_title="Enterprise AI Workflow Router",
        page_icon="🔀",
        layout="wide",
        initial_sidebar_state="expanded",
    )

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
