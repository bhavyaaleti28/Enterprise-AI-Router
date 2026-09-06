"""Domain themes and global application styling."""

import streamlit as st

DOMAIN_THEMES = {
    "HR": {
        "label": "Human Resources",
        "short": "HR",
        "icon": "👥",
        "accent": "#7c3aed",
        "accent_light": "#ede9fe",
        "gradient": "linear-gradient(135deg, #5b21b6 0%, #7c3aed 50%, #a78bfa 100%)",
        "tagline": "Employee services, leave, payroll & benefits",
    },
    "IT_SUPPORT": {
        "label": "IT Support",
        "short": "IT",
        "icon": "💻",
        "accent": "#0284c7",
        "accent_light": "#e0f2fe",
        "gradient": "linear-gradient(135deg, #0369a1 0%, #0284c7 50%, #38bdf8 100%)",
        "tagline": "Password resets, hardware, software & network",
    },
    "FINANCE": {
        "label": "Finance",
        "short": "Finance",
        "icon": "💰",
        "accent": "#059669",
        "accent_light": "#d1fae5",
        "gradient": "linear-gradient(135deg, #047857 0%, #059669 50%, #34d399 100%)",
        "tagline": "Expenses, invoices, budgets & reporting",
    },
    "FACILITIES": {
        "label": "Facilities",
        "short": "Facilities",
        "icon": "🏢",
        "accent": "#d97706",
        "accent_light": "#fef3c7",
        "gradient": "linear-gradient(135deg, #b45309 0%, #d97706 50%, #fbbf24 100%)",
        "tagline": "Maintenance, workspace & office access",
    },
    "OPERATIONS": {
        "label": "Operations",
        "short": "Ops",
        "icon": "⚙️",
        "accent": "#4f46e5",
        "accent_light": "#e0e7ff",
        "gradient": "linear-gradient(135deg, #4338ca 0%, #4f46e5 50%, #818cf8 100%)",
        "tagline": "Business processes & internal documents",
    },
    "LEGAL": {
        "label": "Legal",
        "short": "Legal",
        "icon": "⚖️",
        "accent": "#64748b",
        "accent_light": "#f1f5f9",
        "gradient": "linear-gradient(135deg, #475569 0%, #64748b 50%, #94a3b8 100%)",
        "tagline": "Contracts, compliance & policy review",
    },
    "SECURITY": {
        "label": "Security",
        "short": "Security",
        "icon": "🔒",
        "accent": "#dc2626",
        "accent_light": "#fee2e2",
        "gradient": "linear-gradient(135deg, #b91c1c 0%, #dc2626 50%, #f87171 100%)",
        "tagline": "Incidents, phishing & access control",
    },
    "SALES": {
        "label": "Sales",
        "short": "Sales",
        "icon": "📈",
        "accent": "#db2777",
        "accent_light": "#fce7f3",
        "gradient": "linear-gradient(135deg, #be185d 0%, #db2777 50%, #f472b6 100%)",
        "tagline": "Leads, quotations & customer accounts",
    },
}

DEFAULT_THEME = {
    "label": "Enterprise",
    "short": "Admin",
    "icon": "🔀",
    "accent": "#6366f1",
    "accent_light": "#eef2ff",
    "gradient": "linear-gradient(135deg, #4338ca 0%, #6366f1 50%, #818cf8 100%)",
    "tagline": "Workflow routing & request management",
}


def get_domain_theme(domain):
    return DOMAIN_THEMES.get(domain, DEFAULT_THEME)


def inject_global_css(accent="#6366f1", accent_light="#eef2ff"):
    st_style = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    #MainMenu, footer, header[data-testid="stHeader"] {{
        visibility: hidden;
        height: 0;
    }}

    .block-container {{
        padding-top: 1.5rem;
        max-width: 1200px;
    }}

    /* Login page — wider centre column & compact demo table */
    [data-testid="stExpander"] div[data-testid="stMarkdownContainer"] table {{
        width: 100%;
        font-size: 0.82rem;
        table-layout: fixed;
    }}

    [data-testid="stExpander"] div[data-testid="stMarkdownContainer"] th,
    [data-testid="stExpander"] div[data-testid="stMarkdownContainer"] td {{
        padding: 0.35rem 0.5rem;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }}

    [data-testid="stExpander"] div[data-testid="stMarkdownContainer"] th:nth-child(1),
    [data-testid="stExpander"] div[data-testid="stMarkdownContainer"] td:nth-child(1) {{
        width: 38%;
    }}

    [data-testid="stExpander"] div[data-testid="stMarkdownContainer"] th:nth-child(2),
    [data-testid="stExpander"] div[data-testid="stMarkdownContainer"] td:nth-child(2) {{
        width: 32%;
    }}

    [data-testid="stExpander"] div[data-testid="stMarkdownContainer"] th:nth-child(3),
    [data-testid="stExpander"] div[data-testid="stMarkdownContainer"] td:nth-child(3) {{
        width: 30%;
    }}

    /* Prevent code-block copy widgets in demo account table */
    [data-testid="stExpander"] code {{
        background: transparent;
        padding: 0;
        color: inherit;
        font-family: inherit;
        font-size: inherit;
    }}

    .app-shell {{
        min-height: 100vh;
    }}

    /* Login */
    .login-wrap {{
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 80vh;
    }}

    .login-card {{
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        padding: 2.5rem 2.75rem;
        box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.15);
        max-width: 440px;
        width: 100%;
    }}

    .login-brand {{
        text-align: center;
        margin-bottom: 2rem;
    }}

    .login-logo {{
        width: 56px;
        height: 56px;
        background: linear-gradient(135deg, #4338ca, #6366f1);
        border-radius: 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.75rem;
        margin-bottom: 1rem;
    }}

    .login-title {{
        font-size: 1.5rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0 0 0.35rem 0;
    }}

    .login-subtitle {{
        font-size: 0.9rem;
        color: #64748b;
        margin: 0;
    }}

    /* Demo accounts */
    .demo-accounts-wrap {{
        margin-top: 1.5rem;
        padding-top: 1.25rem;
        border-top: 1px solid #e5e7eb;
    }}

    .demo-accounts-heading {{
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0 0 0.75rem 0;
    }}

    .demo-account-card {{
        display: flex;
        align-items: center;
        gap: 0.85rem;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.75rem 0.9rem;
        margin-bottom: 0.5rem;
        transition: background 0.15s ease, border-color 0.15s ease;
    }}

    .demo-account-card:hover {{
        background: #f1f5f9;
        border-color: #cbd5e1;
    }}

    .demo-account-card.employee {{
        border-left: 3px solid #6366f1;
    }}

    .demo-account-icon {{
        font-size: 1.35rem;
        width: 2.25rem;
        height: 2.25rem;
        display: flex;
        align-items: center;
        justify-content: center;
        background: white;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        flex-shrink: 0;
    }}

    .demo-account-body {{
        flex: 1;
        min-width: 0;
    }}

    .demo-account-label {{
        font-size: 0.82rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0 0 0.3rem 0;
    }}

    .demo-credentials {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
    }}

    .demo-cred-chip {{
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 0.2rem 0.5rem;
        font-size: 0.72rem;
    }}

    .demo-cred-key {{
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.62rem;
        letter-spacing: 0.04em;
    }}

    .demo-cred-val {{
        color: #334155;
        font-family: 'SF Mono', 'Fira Code', monospace;
        font-weight: 600;
        font-size: 0.75rem;
    }}

    .demo-admin-grid {{
        display: grid;
        grid-template-columns: 1fr;
        gap: 0.5rem;
    }}

    /* Hero banner */
    .hero-banner {{
        background: {accent_light};
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 20px;
        padding: 1.75rem 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }}

    .hero-banner::before {{
        content: '';
        position: absolute;
        top: 0; right: 0;
        width: 200px; height: 200px;
        background: {accent};
        opacity: 0.08;
        border-radius: 50%;
        transform: translate(30%, -30%);
    }}

    .hero-icon {{
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }}

    .hero-title {{
        font-size: 1.75rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0 0 0.25rem 0;
    }}

    .hero-tagline {{
        font-size: 0.95rem;
        color: #64748b;
        margin: 0;
    }}

    .hero-badge {{
        display: inline-block;
        background: {accent};
        color: white;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        margin-bottom: 0.75rem;
    }}

    /* Metric cards */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }}

    @media (max-width: 768px) {{
        .metric-grid {{ grid-template-columns: 1fr; }}
    }}

    .metric-card {{
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .metric-card.accent {{
        border-top: 3px solid {accent};
    }}

    .metric-label {{
        font-size: 0.78rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
    }}

    .metric-value {{
        font-size: 2rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1;
    }}

    .metric-icon {{
        font-size: 1.25rem;
        float: right;
        opacity: 0.5;
    }}

    /* Request cards */
    .request-card {{
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: box-shadow 0.15s ease;
    }}

    .request-card:hover {{
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}

    .request-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.75rem;
        gap: 1rem;
    }}

    .request-id {{
        font-size: 0.75rem;
        font-weight: 700;
        color: {accent};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .request-text {{
        font-size: 1rem;
        color: #1e293b;
        line-height: 1.55;
        margin: 0.5rem 0 1rem 0;
    }}

    .request-meta {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
    }}

    .meta-chip {{
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.3rem 0.65rem;
        font-size: 0.78rem;
        font-weight: 500;
        color: #475569;
    }}

    .request-time {{
        font-size: 0.75rem;
        color: #94a3b8;
    }}

    /* Badges */
    .badge {{
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
    }}

    .badge-route {{
        background: #dcfce7;
        color: #166534;
    }}

    .badge-review {{
        background: #fef9c3;
        color: #854d0e;
    }}

    .badge-unrecognised {{
        background: #fee2e2;
        color: #991b1b;
    }}

    .badge-pending {{
        background: #ffedd5;
        color: #c2410c;
    }}

    .badge-resolved {{
        background: #dbeafe;
        color: #1d4ed8;
    }}

    /* Decision result boxes */
    .decision-box {{
        border-radius: 16px;
        padding: 1.5rem 1.75rem;
        margin: 1rem 0;
    }}

    .decision-route {{
        background: linear-gradient(135deg, #ecfdf5, #d1fae5);
        border: 1px solid #6ee7b7;
    }}

    .decision-review {{
        background: linear-gradient(135deg, #fffbeb, #fef3c7);
        border: 1px solid #fcd34d;
    }}

    .decision-unrecognised {{
        background: linear-gradient(135deg, #fef2f2, #fee2e2);
        border: 1px solid #fca5a5;
    }}

    .decision-title {{
        font-size: 1.35rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
    }}

    .decision-route .decision-title {{ color: #065f46; }}
    .decision-review .decision-title {{ color: #92400e; }}
    .decision-unrecognised .decision-title {{ color: #991b1b; }}

    .decision-desc {{
        font-size: 0.95rem;
        margin: 0;
        color: #374151;
        line-height: 1.5;
    }}

    .routing-pill {{
        display: inline-block;
        background: #065f46;
        color: white;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.45rem 1rem;
        border-radius: 999px;
        margin-top: 0.75rem;
    }}

    /* Result fields */
    .result-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1rem 0;
    }}

    .result-field {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.25rem;
    }}

    .result-field-label {{
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.35rem;
    }}

    .result-field-value {{
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
    }}

    /* Workflow pills */
    .workflow-grid {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }}

    .workflow-pill {{
        background: {accent_light};
        color: {accent};
        border: 1px solid rgba(0,0,0,0.06);
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
    }}

    /* Human review panel */
    .review-panel {{
        background: #fffbeb;
        border: 1px solid #fcd34d;
        border-radius: 12px;
        padding: 1.25rem;
        margin-top: 1rem;
    }}

    .review-panel-title {{
        font-size: 0.85rem;
        font-weight: 700;
        color: #92400e;
        margin-bottom: 0.75rem;
    }}

    /* Section headers */
    .section-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {accent_light};
    }}

    /* Empty state */
    .empty-state {{
        text-align: center;
        padding: 3rem 2rem;
        background: #f8fafc;
        border: 2px dashed #e2e8f0;
        border-radius: 16px;
        color: #64748b;
    }}

    .empty-state-icon {{
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
        opacity: 0.5;
    }}

    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background: #0f172a;
    }}

    [data-testid="stSidebar"] * {{
        color: #e2e8f0 !important;
    }}

    [data-testid="stSidebar"] .stRadio label {{
        background: transparent;
        border-radius: 10px;
        padding: 0.5rem 0.75rem;
    }}

    .sidebar-brand {{
        padding: 0.5rem 0 1.5rem 0;
        border-bottom: 1px solid #334155;
        margin-bottom: 1rem;
    }}

    .sidebar-domain-icon {{
        font-size: 2rem;
    }}

    .sidebar-domain-name {{
        font-size: 1.1rem;
        font-weight: 800;
        color: white;
        margin: 0.25rem 0 0 0;
    }}

    .sidebar-user {{
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }}

    /* Filter bar */
    .filter-bar {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.25rem;
    }}

    /* Top user toolbar */
    .user-toolbar {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.65rem 1.25rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .toolbar-user-name {{
        font-size: 0.95rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
    }}

    .toolbar-user-role {{
        font-size: 0.78rem;
        color: #64748b;
        margin: 0.1rem 0 0 0;
    }}

    </style>
    """
    st.markdown(st_style, unsafe_allow_html=True)
