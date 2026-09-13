import streamlit as st
import requests
import pandas as pd


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="LeadFlow",
    page_icon="💰",
    layout="wide",
)


# --------------------------------------------------
# Dark SaaS styling
# --------------------------------------------------

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #0b0f14;
        color: #f1f5f9;
    }

    /* Main content width */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Headings */
    h1, h2, h3 {
        color: #f8fafc !important;
    }

    /* Normal text */
    p, label, .stMarkdown {
        color: #cbd5e1;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 18px;
    }

    div[data-testid="stMetricValue"] {
        color: #f8fafc;
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
    }

    /* Dataframe */
    div[data-testid="stDataFrame"] {
        border: 1px solid #1f2937;
        border-radius: 12px;
        overflow: hidden;
    }

    /* Selectbox */
    div[data-baseweb="select"] > div {
        background-color: #111827;
        border-color: #334155;
        color: #f8fafc;
    }

    /* Info boxes */
    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    /* Success */
    div[data-testid="stAlert"][kind="success"] {
        background-color: #0d2118;
        border: 1px solid #166534;
    }

    /* Warning */
    div[data-testid="stAlert"][kind="warning"] {
        background-color: #211b0d;
        border: 1px solid #854d0e;
    }

    /* Info */
    div[data-testid="stAlert"][kind="info"] {
        background-color: #111c2e;
        border: 1px solid #1e40af;
    }

    /* Buttons */
    .stButton > button {
        background-color: #16a34a;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #15803d;
        color: white;
    }

    /* Divider */
    hr {
        border-color: #1f2937;
    }

    /* Caption */
    .stCaption {
        color: #64748b !important;
    }

    /* Custom hero */
    .hero {
        background: linear-gradient(
            135deg,
            #111827 0%,
            #0f172a 100%
        );
        border: 1px solid #1f2937;
        border-radius: 18px;
        padding: 30px;
        margin-bottom: 25px;
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 1rem;
        color: #94a3b8;
    }

    /* Section cards */
    .section-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# API
# --------------------------------------------------

API_URL = "http://127.0.0.1:8000/api/opportunities"


# --------------------------------------------------
# Load opportunities
# --------------------------------------------------

@st.cache_data(ttl=30)
def get_opportunities():

    response = requests.get(
        API_URL,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return pd.DataFrame(data["opportunities"])


# --------------------------------------------------
# Hero
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">
            💰 LeadFlow
        </div>
        <div class="hero-subtitle">
            AI Revenue Recovery for E-commerce
            <br>
            Identify high-intent shoppers, understand purchase barriers,
            and prioritize the next best action.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Load data
# --------------------------------------------------

try:

    df = get_opportunities()

except Exception as e:

    st.error(
        "Unable to connect to the LeadFlow API."
    )

    st.code(str(e))

    st.stop()


# --------------------------------------------------
# Metrics
# --------------------------------------------------

high_intent = len(
    df[df["intent_level"] == "High"]
)

checkout = len(
    df[df["purchase_stage"] == "Checkout"]
)

not_purchased = len(
    df[df["purchase_status"] == "Not Purchased"]
)

potential_revenue = df.loc[
    df["purchase_status"] == "Not Purchased",
    "cart_value"
].sum()


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "🔥 High Intent",
        high_intent,
    )


with col2:

    st.metric(
        "🛒 Checkout",
        checkout,
    )


with col3:

    st.metric(
        "⚠️ Unconverted",
        not_purchased,
    )


with col4:

    st.metric(
        "💰 Potential Cart Value",
        f"₹{potential_revenue:,.0f}",
    )


st.divider()


# --------------------------------------------------
# Opportunity filters
# --------------------------------------------------

st.subheader("🔥 Priority Opportunities")

st.caption(
    "Filter shoppers by purchase intent, barrier, and buying stage."
)


filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)


with filter_col1:

    intent_filter = st.selectbox(
        "Intent",
        ["All", "High", "Medium", "Low"],
    )


with filter_col2:

    barrier_options = [
        "All"
    ] + sorted(
        df["barrier"].dropna().unique().tolist()
    )

    barrier_filter = st.selectbox(
        "Barrier",
        barrier_options,
    )


with filter_col3:

    stage_options = [
        "All"
    ] + sorted(
        df["purchase_stage"].dropna().unique().tolist()
    )

    stage_filter = st.selectbox(
        "Purchase Stage",
        stage_options,
    )


with filter_col4:

    status_filter = st.selectbox(
        "Purchase Status",
        [
            "Not Purchased",
            "Purchased",
            "All",
        ],
    )


# --------------------------------------------------
# Apply filters
# --------------------------------------------------

filtered_df = df.copy()


if intent_filter != "All":

    filtered_df = filtered_df[
        filtered_df["intent_level"] == intent_filter
    ]


if barrier_filter != "All":

    filtered_df = filtered_df[
        filtered_df["barrier"] == barrier_filter
    ]


if stage_filter != "All":

    filtered_df = filtered_df[
        filtered_df["purchase_stage"] == stage_filter
    ]


if status_filter != "All":

    filtered_df = filtered_df[
        filtered_df["purchase_status"] == status_filter
    ]


# --------------------------------------------------
# Priority opportunities
# --------------------------------------------------

priority_df = df[
    (df["intent_level"] == "High")
    & (df["purchase_status"] == "Not Purchased")
].copy()

priority_df = priority_df.sort_values(
    by=["intent_score", "cart_value"],
    ascending=[False, False],
)


# --------------------------------------------------
# Opportunity table
# --------------------------------------------------

if filtered_df.empty:

    st.info(
        "No shoppers match the selected filters."
    )

else:

    display_columns = [
        "customer_name",
        "product_name",
        "cart_value",
        "intent_score",
        "intent_level",
        "barrier",
        "purchase_stage",
        "urgency",
        "purchase_status",
    ]

    display_df = filtered_df[
        display_columns
    ].copy()

    display_df = display_df.rename(
        columns={
            "customer_name": "Shopper",
            "product_name": "Product",
            "cart_value": "Cart Value",
            "intent_score": "Intent Score",
            "intent_level": "Intent",
            "barrier": "Barrier",
            "purchase_stage": "Stage",
            "urgency": "Urgency",
            "purchase_status": "Status",
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )


st.divider()


# --------------------------------------------------
# Shopper analysis
# --------------------------------------------------

st.subheader("🔎 Opportunity Details")


shopper_options = (
    priority_df["customer_name"].tolist()
    if not priority_df.empty
    else df["customer_name"].tolist()
)


selected_customer = st.selectbox(
    "Select a shopper",
    shopper_options,
)


selected = df[
    df["customer_name"] == selected_customer
].iloc[0]


# --------------------------------------------------
# Why this shopper matters
# --------------------------------------------------

st.markdown("### 🎯 Why this shopper matters")


intent = selected["intent_level"]
score = int(selected["intent_score"])
stage = selected["purchase_stage"]
barrier = selected["barrier"]
cart_value = float(selected["cart_value"])
status = selected["purchase_status"]


if status == "Purchased":

    st.info(
        "This shopper has already purchased. "
        "Use their history for retention or future recommendations."
    )

elif intent == "High":

    st.success(
        f"High-intent shopper with a ₹{cart_value:,.0f} "
        f"purchase opportunity currently at the {stage.lower()} stage."
    )

elif intent == "Medium":

    st.warning(
        f"Medium-intent shopper currently in the "
        f"{stage.lower()} stage. Nurturing may increase conversion."
    )

else:

    st.info(
        "Low-intent shopper. No immediate sales intervention is recommended."
    )


# --------------------------------------------------
# Shopper information
# --------------------------------------------------

col1, col2 = st.columns(2)


with col1:

    st.markdown("### 👤 Shopper")

    st.write(
        f"**Name:** {selected['customer_name']}"
    )

    st.write(
        f"**Customer Type:** {selected['customer_type']}"
    )

    st.write(
        f"**Channel:** {selected['channel']}"
    )

    st.write(
        f"**Previous Orders:** {selected['previous_orders']}"
    )

    st.write(
        f"**Previous Spend:** "
        f"₹{float(selected['previous_spend']):,.0f}"
    )


with col2:

    st.markdown("### 🛍️ Purchase Opportunity")

    st.write(
        f"**Product:** {selected['product_name']}"
    )

    st.write(
        f"**Cart Value:** ₹{cart_value:,.0f}"
    )

    st.write(
        f"**Intent:** {intent} ({score}/100)"
    )

    st.write(
        f"**Barrier:** {barrier}"
    )

    st.write(
        f"**Stage:** {stage}"
    )

    st.write(
        f"**Urgency:** {selected['urgency']}"
    )


# --------------------------------------------------
# Customer message
# --------------------------------------------------

st.markdown("### 💬 Customer Message")

st.info(
    selected["message"]
)


# --------------------------------------------------
# Recommended action
# --------------------------------------------------

st.markdown("### 🚀 Recommended Next Action")

action = selected["recommended_action"]


if isinstance(action, dict):

    action_text = action.get(
        "description",
        str(action),
    )

else:

    action_text = str(action)


st.success(action_text)


# --------------------------------------------------
# Recommended offer
# --------------------------------------------------

offer = selected["recommended_offer"]

st.markdown("### 🏷️ Offer Recommendation")


if isinstance(offer, str) and offer:

    st.warning(offer)

elif isinstance(offer, dict):

    st.warning(
        f"**{offer.get('type', 'Offer')}** — "
        f"{offer.get('description', '')}"
    )

else:

    st.caption(
        "No discount offer recommended. "
        "LeadFlow only recommends offers when the shopper "
        "meets the configured business rules."
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "LeadFlow Demo • Synthetic E-commerce Data • "
    "AI-Assisted Revenue Recovery"
)