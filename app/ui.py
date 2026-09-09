import sqlite3

import streamlit as st

from app.database import create_database, save_lead
from app.main import (
    calculate_score,
    determine_action,
    determine_priority,
    extract_lead_information,
    generate_follow_up,
)


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

DATABASE_NAME = "leads.db"

create_database()


def get_leads():

    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row

    rows = connection.execute(
        """
        SELECT
            id,
            name,
            company,
            message,
            lead_score,
            priority,
            action,
            requirement,
            created_at
        FROM leads
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


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
    "# Turn incoming enquiries into sales-ready opportunities."
)

st.markdown(
    "LeadFlow reads customer enquiries, identifies buying signals, "
    "scores the opportunity, and tells your sales team what to do next."
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
# MAIN WORKSPACE
# =========================================================

input_col, result_col = st.columns(
    [1.05, 0.95],
    gap="large",
)


# =========================================================
# NEW LEAD
# =========================================================

with input_col:

    with st.container(border=True):

        st.markdown("### New lead")

        st.caption(
            "Paste a customer enquiry to qualify it instantly."
        )

        name = st.text_input(
            "Lead name",
            placeholder="e.g. Priya Sharma",
        )

        company = st.text_input(
            "Company",
            placeholder="e.g. Acme Technologies",
        )

        message = st.text_area(
            "Customer enquiry",
            placeholder=(
                "Paste the customer's message here...\n\n"
                "Example: We need 200 licenses and our budget is ₹10 lakh."
            ),
        )

        analyze = st.button(
            "Analyze lead →",
            type="primary",
        )


# =========================================================
# LEAD ASSESSMENT
# =========================================================

with result_col:

    with st.container(border=True):

        st.markdown("### Lead assessment")

        if analyze:

            if (
                not name.strip()
                or not company.strip()
                or not message.strip()
            ):

                st.warning(
                    "Please provide the lead name, company, and enquiry."
                )

            else:

                with st.spinner(
                    "Analyzing enquiry..."
                ):

                    try:

                        # -----------------------------------------
                        # AI EXTRACTION
                        # -----------------------------------------

                        info = extract_lead_information(
                            message.strip()
                        )


                        # -----------------------------------------
                        # SCORING
                        # -----------------------------------------

                        score = calculate_score(
                            info
                        )


                        # -----------------------------------------
                        # PRIORITY
                        # -----------------------------------------

                        priority = determine_priority(
                            score
                        )


                        # -----------------------------------------
                        # ACTION
                        # -----------------------------------------

                        action = determine_action(
                            score,
                            info.get(
                                "missing_information",
                                [],
                            ),
                            message.strip(),
                        )


                        # -----------------------------------------
                        # AI FOLLOW-UP
                        # -----------------------------------------

                        follow_up = generate_follow_up(
                            name.strip(),
                            company.strip(),
                            message.strip(),
                            info,
                            score,
                            priority,
                        )


                        # -----------------------------------------
                        # SAVE LEAD
                        # -----------------------------------------

                        save_lead(
                            name=name.strip(),
                            company=company.strip(),
                            message=message.strip(),
                            lead_score=score,
                            priority=priority,
                            action=action,
                            requirement=info.get(
                                "requirement",
                                "No requirement provided.",
                            ),
                        )


                        # -----------------------------------------
                        # SESSION STATE
                        # -----------------------------------------

                        st.session_state["analysis"] = {
                            "name": name.strip(),
                            "company": company.strip(),
                            "message": message.strip(),
                            "info": info,
                            "score": score,
                            "priority": priority,
                            "action": action,
                            "follow_up": follow_up,
                        }


                        st.rerun()


                    except RuntimeError as error:

                        st.error(
                            str(error)
                        )


                    except ValueError as error:

                        st.error(
                            str(error)
                        )


                    except Exception as error:

                        st.error(
                            f"Something went wrong: {error}"
                        )


        # =====================================================
        # RESULT
        # =====================================================

        analysis = st.session_state.get(
            "analysis"
        )


        if analysis:

            score = analysis["score"]

            priority = analysis["priority"]

            action = analysis["action"]

            info = analysis["info"]


            st.caption(
                f"{analysis['name']} · "
                f"{analysis['company']}"
            )


            st.write("")


            score_col, priority_col = st.columns(
                [1, 1]
            )


            with score_col:

                st.metric(
                    "Lead score",
                    f"{score}/100",
                )


            with priority_col:

                st.metric(
                    "Priority",
                    priority,
                )


            st.write("")


            # ---------------------------------------------
            # ACTION
            # ---------------------------------------------

            st.markdown(
                "#### Recommended action"
            )


            if priority == "High":

                st.error(
                    f"🔥 {action}"
                )

            elif priority == "Medium":

                st.warning(
                    f"⚡ {action}"
                )

            else:

                st.info(
                    f"ℹ️ {action}"
                )


            st.write("")


            # ---------------------------------------------
            # REQUIREMENT
            # ---------------------------------------------

            st.markdown(
                "#### Requirement"
            )


            st.write(
                info.get(
                    "requirement",
                    "No requirement identified.",
                )
            )


            # ---------------------------------------------
            # FOLLOW-UP
            # ---------------------------------------------

            st.write("")

            st.markdown(
                "#### Suggested follow-up"
            )

            st.caption(
                "AI-generated response based on the customer's enquiry."
            )

            st.code(
                analysis["follow_up"],
                language=None,
            )


        else:

            st.info(
                "Submit a customer enquiry to generate "
                "a lead assessment."
            )


# =========================================================
# BUYING SIGNALS + MISSING INFORMATION
# =========================================================

st.write("")
st.write("")


signals_col, missing_col = st.columns(
    2,
    gap="large",
)


analysis = st.session_state.get(
    "analysis"
)


# =========================================================
# BUYING SIGNALS
# =========================================================

with signals_col:

    with st.container(border=True):

        st.markdown(
            "### Buying signals"
        )

        st.caption(
            "Signals explicitly detected in the customer's enquiry."
        )


        if analysis:

            info = analysis["info"]


            signals = [

                (
                    "Purchase intent",
                    info.get(
                        "purchase_intent",
                        False,
                    ),
                ),

                (
                    "Specific product / service",
                    info.get(
                        "specific_product_or_service",
                        False,
                    ),
                ),

                (
                    "Quantity / scope",
                    info.get(
                        "quantity_or_scope",
                        False,
                    ),
                ),

                (
                    "Budget",
                    info.get(
                        "budget",
                        False,
                    ),
                ),

                (
                    "Purchase timeline",
                    info.get(
                        "purchase_timeline",
                        False,
                    ),
                ),

                (
                    "Decision-maker",
                    info.get(
                        "decision_making_authority",
                        False,
                    ),
                ),

            ]


            for label, present in signals:

                if present:

                    st.success(
                        f"✓ {label}"
                    )

                else:

                    st.caption(
                        f"○ {label}"
                    )


        else:

            st.caption(
                "Analyze a lead to see its buying signals."
            )


# =========================================================
# MISSING INFORMATION
# =========================================================

with missing_col:

    with st.container(border=True):

        st.markdown(
            "### Missing information"
        )

        st.caption(
            "Details the salesperson may need before qualification."
        )


        if analysis:

            missing = analysis["info"].get(
                "missing_information",
                [],
            )


            if missing:

                for item in missing:

                    # Make internal AI field names readable
                    readable_item = str(item).replace(
                        "_",
                        " ",
                    ).title()

                    st.warning(
                        f"• {readable_item}"
                    )


            else:

                st.success(
                    "No major missing information detected."
                )


        else:

            st.caption(
                "Analyze a lead to identify missing information."
            )


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