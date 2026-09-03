import json
import streamlit as st

from router.classifier import classify_request
from router.decision import make_decision
from router.router import route_request


# -----------------------------
# Page configuration
# -----------------------------

st.set_page_config(
    page_title="Enterprise AI Workflow Router",
    page_icon="🔀",
    layout="centered"
)


# -----------------------------
# Custom styling
# -----------------------------

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
    unsafe_allow_html=True
)


# -----------------------------
# Header
# -----------------------------

st.markdown(
    '<div class="main-title">Enterprise AI Workflow Router</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Classify an enterprise request and route it to the appropriate workflow.'
    '</div>',
    unsafe_allow_html=True
)


# -----------------------------
# Example requests
# -----------------------------

st.markdown("### Try an example")

example = st.selectbox(
    "Select a sample request",
    [
        "Choose an example...",
        "I forgot my company password.",
        "I want to apply for leave.",
        "The AC in my office is broken."
    ]
)

# -----------------------------
# Request input
# -----------------------------

request = st.text_area(
    "Enter your request",
    value="" if example == "Choose an example..." else example,
    placeholder="Example: I forgot my company password.",
    height=120
)


classify_button = st.button(
    "Classify Request",
    type="primary",
    use_container_width=False
)


# -----------------------------
# Classification
# -----------------------------

if classify_button:

    if not request.strip():

        st.warning("Please enter a request.")

    else:

        with st.spinner("Classifying request..."):

            classification = classify_request(request)

            decision = make_decision(
                classification,
                request
            )

            routing = route_request(
                decision,
                classification
            )

        try:
            result = json.loads(classification)

            domain = result.get("domain")
            workflow = result.get("workflow")

        except json.JSONDecodeError:

            domain = None
            workflow = None

        # -----------------------------
        # Results
        # -----------------------------

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                '<div class="result-label">Domain</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="result-value">'
                f'{domain if domain else "—"}'
                f'</div>',
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                '<div class="result-label">Workflow</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="result-value">'
                f'{workflow if workflow else "—"}'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown("### Decision")

        # -----------------------------
        # ROUTE
        # -----------------------------

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
                unsafe_allow_html=True
            )

            st.markdown(
                f"**Routing:** `{domain} → {workflow}`"
            )

        # -----------------------------
        # HUMAN REVIEW
        # -----------------------------

        elif decision == "HUMAN_REVIEW":

            st.markdown(
                """
                <div class="review-box">
                    <div class="decision-text">⚠ HUMAN REVIEW</div>
                    <div class="info-text">
                        The request belongs to an enterprise area,
                        but the specific workflow is not clear enough
                        for automatic routing.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if domain:
                st.markdown(
                    f"**Detected domain:** `{domain}`"
                )

        # -----------------------------
        # UNRECOGNISED
        # -----------------------------

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
                unsafe_allow_html=True
            )

        else:

            st.info(f"Decision: {decision}")


# -----------------------------
# Footer
# -----------------------------

st.divider()

st.caption(
    "Enterprise AI Workflow Router • Powered by Ollama and Llama 3:8B"
)