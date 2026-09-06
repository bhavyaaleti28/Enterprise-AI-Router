"""Reusable UI components for the Streamlit application."""

import streamlit as st

from ui.theme import get_domain_theme


def status_badge(status):
    styles = {
        "ROUTED": ("badge-route", "Routed"),
        "HUMAN_REVIEW": ("badge-review", "Human Review"),
        "WAITING_FOR_INFORMATION": ("badge-pending", "Waiting for Info"),
        "IN_PROGRESS": ("badge-resolved", "In Progress"),
        "COMPLETED": ("badge-route", "Completed"),
        "REJECTED": ("badge-unrecognised", "Rejected"),
        "UNRECOGNISED": ("badge-unrecognised", "Unrecognised"),
    }
    css, label = styles.get(status, ("badge", status or "Unknown"))
    return f'<span class="badge {css}">{label}</span>'


def decision_badge(decision, review_status=None, status=None):
    if status:
        return status_badge(status)
    if review_status == "RESOLVED":
        return '<span class="badge badge-resolved">Resolved</span>'
    if decision == "ROUTE":
        return '<span class="badge badge-route">Routed</span>'
    if decision == "HUMAN_REVIEW":
        if review_status == "PENDING":
            return '<span class="badge badge-pending">Pending Review</span>'
        return '<span class="badge badge-review">Human Review</span>'
    if decision == "UNRECOGNISED":
        return '<span class="badge badge-unrecognised">Unrecognised</span>'
    return f'<span class="badge">{decision}</span>'


def render_metric_cards(counts):
    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-card accent">
                <span class="metric-icon">📋</span>
                <div class="metric-label">Total Requests</div>
                <div class="metric-value">{counts['total']}</div>
            </div>
            <div class="metric-card accent">
                <span class="metric-icon">✅</span>
                <div class="metric-label">Routed</div>
                <div class="metric-value">{counts['routed']}</div>
            </div>
            <div class="metric-card accent">
                <span class="metric-icon">👁</span>
                <div class="metric-label">Human Review</div>
                <div class="metric-value">{counts['human_review']}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero_banner(domain):
    theme = get_domain_theme(domain)
    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-badge">{theme['short']} Dashboard</div>
            <div class="hero-icon">{theme['icon']}</div>
            <h1 class="hero-title">{theme['label']}</h1>
            <p class="hero-tagline">{theme['tagline']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_workflow_pills(workflows, domain):
    if not workflows:
        st.info("No workflows configured for this domain.")
        return

    pills = "".join(
        f'<span class="workflow-pill">{wf.replace("_", " ").title()}</span>'
        for wf in workflows
    )
    st.markdown(
        f'<div class="workflow-grid">{pills}</div>',
        unsafe_allow_html=True,
    )


def render_request_card_html(row):
    (
        request_id,
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
        updated_at,
    ) = row

    wf_display = (workflow or reviewed_workflow or "—").replace("_", " ").title()
    badge = status_badge(status) if status else decision_badge(decision, review_status)

    extra_notes = ""
    if review_status == "RESOLVED" and reviewed_workflow:
        extra_notes += (
            f'<div style="margin-top:0.75rem;padding:0.5rem 0.75rem;'
            f'background:#dbeafe;border-radius:8px;font-size:0.82rem;'
            f'color:#1d4ed8;font-weight:600;">'
            f'✓ Resolved via human review → '
            f'{reviewed_workflow.replace("_", " ").title()}'
            f'</div>'
        )
    if clarification_message:
        extra_notes += (
            f'<div style="margin-top:0.75rem;padding:0.5rem 0.75rem;'
            f'background:#fffbeb;border-radius:8px;font-size:0.82rem;'
            f'color:#92400e;">'
            f'<strong>Clarification requested:</strong> {clarification_message}'
            f'</div>'
        )
    if employee_response:
        extra_notes += (
            f'<div style="margin-top:0.75rem;padding:0.5rem 0.75rem;'
            f'background:#ecfdf5;border-radius:8px;font-size:0.82rem;'
            f'color:#065f46;">'
            f'<strong>Employee response:</strong> {employee_response}'
            f'</div>'
        )
    if rejection_reason:
        extra_notes += (
            f'<div style="margin-top:0.75rem;padding:0.5rem 0.75rem;'
            f'background:#fef2f2;border-radius:8px;font-size:0.82rem;'
            f'color:#991b1b;">'
            f'<strong>Rejection reason:</strong> {rejection_reason}'
            f'</div>'
        )

    time_label = updated_at or created_at
    submitter = f" · 👤 {submitted_by}" if submitted_by else ""

    st.markdown(
        f"""
        <div class="request-card">
            <div class="request-header">
                <span class="request-id">Request #{request_id}</span>
                {badge}
            </div>
            <p class="request-text">{request_text}</p>
            <div class="request-meta">
                <span class="meta-chip">🏷 {domain or "—"}</span>
                <span class="meta-chip">⚡ {wf_display}</span>
            </div>
            <div class="request-time">🕐 {time_label}{submitter}</div>
            {extra_notes}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(icon, title, message):
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-state-icon">{icon}</div>
            <strong>{title}</strong><br>{message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_decision_result(decision, domain=None, workflow=None):
    if decision == "ROUTE":
        routing = f"{domain} → {workflow}".replace("_", " ")
        st.markdown(
            f"""
            <div class="decision-box decision-route">
                <div class="decision-title">✓ ROUTE</div>
                <p class="decision-desc">
                    Request can be safely routed to the selected workflow.
                </p>
                <span class="routing-pill">{routing}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif decision == "HUMAN_REVIEW":
        st.markdown(
            """
            <div class="decision-box decision-review">
                <div class="decision-title">⚠ HUMAN REVIEW</div>
                <p class="decision-desc">
                    The request belongs to an enterprise area, but the specific
                    workflow is not clear enough for automatic routing.
                    A domain administrator will review and route it.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if domain:
            st.markdown(
                f"**Detected domain:** `{domain}`"
            )
    elif decision == "UNRECOGNISED":
        st.markdown(
            """
            <div class="decision-box decision-unrecognised">
                <div class="decision-title">✕ UNRECOGNISED</div>
                <p class="decision-desc">
                    This request does not match any supported enterprise
                    workflow category.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_classification_fields(domain, workflow):
    st.markdown(
        f"""
        <div class="result-grid">
            <div class="result-field">
                <div class="result-field-label">Domain</div>
                <div class="result-field-value">{domain or "—"}</div>
            </div>
            <div class="result-field">
                <div class="result-field-label">Workflow</div>
                <div class="result-field-value">
                    {(workflow or "—").replace("_", " ").title()}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_branding():
    st.markdown(
        """
        <div class="login-brand">
            <div class="login-logo">🔀</div>
            <h1 class="login-title">Enterprise AI Router</h1>
            <p class="login-subtitle">
                Intelligent workflow classification &amp; routing
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_demo_accounts(accounts):
    rows = []
    for username, password, domain, role, _label in accounts:
        if role == "EMPLOYEE":
            display = "Employee"
        else:
            theme = get_domain_theme(domain)
            display = f"{theme['short']} Admin"

        rows.append(f"| {display} | {username} | {password} |")

    table = "\n".join([
        "| Role | Username | Password |",
        "|:-----|:---------|:---------|",
        *rows,
    ])

    st.markdown(table)


def render_sidebar_brand(domain, username):
    theme = get_domain_theme(domain)
    st.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="sidebar-domain-icon">{theme['icon']}</div>
            <div class="sidebar-domain-name">{theme['label']}</div>
            <div class="sidebar-user">Signed in as {username}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_user_toolbar(username, domain=None, role=None):
    """Top bar with user info and logout. Returns True if logout was clicked."""
    if role == "DOMAIN_ADMIN" and domain:
        theme = get_domain_theme(domain)
        role_label = f"{theme['label']} Administrator"
    elif role == "EMPLOYEE":
        role_label = "Employee"
    else:
        role_label = role or "User"

    st.markdown('<div class="user-toolbar">', unsafe_allow_html=True)
    info_col, btn_col = st.columns([5, 1])
    with info_col:
        st.markdown(
            f"""
            <p class="toolbar-user-name">👤 {username}</p>
            <p class="toolbar-user-role">{role_label}</p>
            """,
            unsafe_allow_html=True,
        )
    with btn_col:
        logout = st.button(
            "Logout",
            key="toolbar_logout",
            type="primary",
            use_container_width=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
    return logout
