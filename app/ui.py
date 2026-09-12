import requests

import streamlit as st



# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="LeadFlow — AI Lead Qualification",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# DATABASE
# =========================================================

API_URL = "https://ai-lead-automation-cm4y.onrender.com/api/leads"


def get_leads():

    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    return response.json()


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ================= APP ================= */

    .stApp {
        background:
            radial-gradient(
                circle at 15% 0%,
                rgba(99, 102, 241, 0.13),
                transparent 32%
            ),
            radial-gradient(
                circle at 90% 10%,
                rgba(139, 92, 246, 0.10),
                transparent 28%
            ),
            #09090b;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
    }


    /* ================= TYPOGRAPHY ================= */

    h1,
    h2,
    h3 {
        letter-spacing: -0.03em;
    }

    p,
    label {
        color: #a1a1aa;
    }


    /* ================= INPUTS ================= */

    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {
        background: #111114 !important;
        border-color: #27272a !important;
    }

    input,
    textarea {
        color: #f4f4f5 !important;
    }

    textarea {
        min-height: 150px !important;
    }


    /* ================= BUTTON ================= */

    .stButton > button {
        width: 100%;
        min-height: 48px;
        border-radius: 10px;
        border: 1px solid #6366f1;
        background: #6366f1;
        color: white;
        font-size: 1rem;
        font-weight: 700;
        transition: 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #818cf8;
        background: #4f46e5;
        transform: translateY(-1px);
    }


    /* ================= METRICS ================= */

    div[data-testid="stMetric"] {
        background: #111114;
        border: 1px solid #27272a;
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
    }

    div[data-testid="stMetricLabel"] {
        color: #a1a1aa;
    }

    div[data-testid="stMetricValue"] {
        color: #fafafa;
        font-size: 2rem;
        font-weight: 750;
    }


    /* ================= CONTAINERS ================= */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #27272a !important;
        background: rgba(17, 17, 20, 0.72);
        border-radius: 16px;
    }


    /* ================= DIVIDER ================= */

    hr {
        border-color: #27272a;
    }


    /* ================= SMALL TEXT ================= */

    .muted {
        color: #71717a;
        font-size: 0.86rem;
    }


    /* ================= FOLLOW-UP ================= */

    .followup-label {
        color: #a1a1aa;
        font-size: 0.86rem;
        margin-bottom: 0.4rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

header_left, header_right = st.columns([4, 1])

with header_left:

    st.markdown(
        "### ⚡ **LeadFlow**"
    )

    st.caption(
        "AI-powered lead qualification for faster sales follow-up"
    )


with header_right:

    st.markdown(
        "<div style='text-align:right; padding-top:12px;'>"
        "🟢 System operational"
        "</div>",
        unsafe_allow_html=True,
    )


st.divider()


# =========================================================
# HERO
# =========================================================

st.markdown(
    "# Turn inbound enquiries into sales-ready opportunities."
)

st.markdown(
    "LeadFlow helps sales teams respond faster by automatically "
    "understanding incoming enquiries, identifying buying signals, "
    "prioritizing opportunities, and drafting the next response."
)

st.caption(
    "Live workflow: Website enquiry → AI qualification → Sales dashboard"
)

st.write("")
st.write("")


# =========================================================
# DASHBOARD METRICS
# =========================================================

leads = get_leads()

total_leads = len(leads)

high_count = sum(
    1
    for lead in leads
    if lead["priority"] == "High"
)

medium_count = sum(
    1
    for lead in leads
    if lead["priority"] == "Medium"
)

average_score = (
    sum(lead["lead_score"] for lead in leads)
    / total_leads
    if total_leads
    else 0
)


metric1, metric2, metric3, metric4 = st.columns(4)


with metric1:

    st.metric(
        "Leads processed",
        total_leads,
    )


with metric2:

    st.metric(
        "High priority",
        high_count,
    )


with metric3:

    st.metric(
        "Medium priority",
        medium_count,
    )


with metric4:

    st.metric(
        "Average score",
        f"{average_score:.1f}",
    )


st.write("")
st.write("")


# =========================================================
# LIVE LEADS
# =========================================================

st.markdown("### Live sales activity")
st.caption("Real enquiries received through the LeadFlow website.")

# =========================================================
# RECENT LEADS
# =========================================================

st.write("")
st.write("")


st.markdown(
    "### Recent leads"
)

st.caption(
    "Latest enquiries processed by LeadFlow."
)


recent_leads = get_leads()


if recent_leads:

    for lead in recent_leads[:8]:

        with st.container(border=True):

            col1, col2, col3, col4 = st.columns(
                [2.5, 2.1, 1.1, 3.5]
            )

            # ---------------------------------------------
            # NAME / COMPANY
            # ---------------------------------------------

            with col1:

                st.markdown(
                    f"**{lead['name']}**"
                )

                st.caption(
                    lead["company"]
                )

            # ---------------------------------------------
            # PRIORITY
            # ---------------------------------------------

            with col2:

                if lead["priority"] == "High":

                    st.error(
                        "HIGH",
                        icon="🔥",
                    )

                elif lead["priority"] == "Medium":

                    st.warning(
                        "MEDIUM",
                        icon="⚡",
                    )

                else:

                    st.info(
                        "LOW",
                        icon="ℹ️",
                    )

            # ---------------------------------------------
            # SCORE
            # ---------------------------------------------

            with col3:

                st.metric(
                    "Score",
                    f"{lead['lead_score']}",
                )

            # ---------------------------------------------
            # ACTION
            # ---------------------------------------------

            with col4:

                st.caption(
                    "Next action"
                )

                st.write(
                    lead["action"]
                )

else:

    st.info(
        "No leads have been processed yet."
    )


# =========================================================
# FOOTER
# =========================================================

st.write("")
st.divider()


footer_left, footer_right = st.columns(
    [3, 1]
)


with footer_left:

    st.caption(
        "LeadFlow · AI-assisted sales qualification"
    )


with footer_right:

    st.caption(
        "Built for faster sales response"
    )