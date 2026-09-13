import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found. Make sure it is present in your .env file."
    )

groq_client = Groq(api_key=GROQ_API_KEY)

GROQ_MODEL = "openai/gpt-oss-20b"


def analyze_shopper(shopper):
    """
    Analyze an e-commerce shopper and determine:

    - Purchase intent
    - Buying signals
    - Purchase barrier
    - Purchase stage
    - Urgency
    - Recommended action
    - Recommended offer
    """

    # ==================================================
    # 1. READ SHOPPER DATA
    # ==================================================

    views = int(shopper.get("product_views", 0))
    added_to_cart = bool(shopper.get("added_to_cart", False))
    checkout_started = bool(shopper.get("checkout_started", False))
    previous_orders = int(shopper.get("previous_orders", 0))
    previous_spend = float(shopper.get("previous_spend", 0))
    cart_value = float(shopper.get("cart_value", 0))

    purchase_status = str(
        shopper.get("purchase_status", "Not Purchased")
    ).strip()

    message = str(
        shopper.get("message", "")
    ).strip()

    message_lower = message.lower()

    # ==================================================
    # 2. CALCULATE PURCHASE INTENT
    # ==================================================

    score = 0
    buying_signals = []

    # Repeated product interest
    if views >= 5:
        score += 20
        buying_signals.append("Repeated product views")

    elif views >= 3:
        score += 12
        buying_signals.append("Multiple product views")

    # Added to cart
    if added_to_cart:
        score += 25
        buying_signals.append("Added product to cart")

    # Started checkout
    if checkout_started:
        score += 35
        buying_signals.append("Started checkout")

    # Returning customer
    if previous_orders >= 1:
        score += 10
        buying_signals.append("Returning customer")

    # High-value cart
    if cart_value >= 10000:
        score += 10
        buying_signals.append("High-value cart")

    # Cap score at 100
    score = min(score, 100)

    # Determine intent level
    if score >= 75:
        intent_level = "High"

    elif score >= 45:
        intent_level = "Medium"

    else:
        intent_level = "Low"

    # ==================================================
    # 3. IDENTIFY PURCHASE BARRIER
    # ==================================================

    if any(
        word in message_lower
        for word in [
            "deliver",
            "delivery",
            "reach",
            "arrive",
            "shipping",
        ]
    ):
        barrier = "Delivery"

    elif any(
        word in message_lower
        for word in [
            "discount",
            "offer",
            "price",
            "cost",
            "expensive",
            "cheap",
        ]
    ):
        barrier = "Price"

    elif any(
        word in message_lower
        for word in [
            "match",
            "shade",
            "color",
            "colour",
        ]
    ):
        barrier = "Color matching"

    elif any(
        word in message_lower
        for word in [
            "which",
            "suit",
            "suitable",
            "best for",
            "recommend",
        ]
    ):
        barrier = "Product suitability"

    elif any(
        word in message_lower
        for word in [
            "quality",
            "human hair",
            "last",
            "heat",
            "style",
        ]
    ):
        barrier = "Product quality"

    elif any(
        word in message_lower
        for word in [
            "return",
            "refund",
            "exchange",
        ]
    ):
        barrier = "Returns"

    elif any(
        word in message_lower
        for word in [
            "cod",
            "cash on delivery",
            "upi",
            "payment",
            "emi",
        ]
    ):
        barrier = "Payment"

    elif any(
        word in message_lower
        for word in [
            "stock",
            "available",
            "availability",
        ]
    ):
        barrier = "Availability"

    else:
        barrier = "No clear barrier"

    # ==================================================
    # 4. DETERMINE PURCHASE STAGE
    # ==================================================

    if checkout_started:
        purchase_stage = "Checkout"

    elif added_to_cart:
        purchase_stage = "Cart"

    elif views >= 3:
        purchase_stage = "Consideration"

    else:
        purchase_stage = "Discovery"

    # ==================================================
    # 5. DETERMINE URGENCY
    # ==================================================

    urgency_words = [
        "today",
        "tomorrow",
        "friday",
        "saturday",
        "sunday",
        "wedding",
        "urgent",
        "asap",
        "soon",
        "deadline",
    ]

    if any(
        word in message_lower
        for word in urgency_words
    ):
        urgency = "High"

    else:
        urgency = "Normal"

    # ==================================================
    # 6. RECOMMEND NEXT ACTION
    # ==================================================

    if barrier == "Delivery":

        recommended_action = (
            "Confirm delivery availability and expected delivery date"
        )

    elif barrier == "Price":

        recommended_action = (
            "Address the price concern and share applicable offers"
        )

    elif barrier == "Color matching":

        recommended_action = (
            "Help the shopper choose the closest color match"
        )

    elif barrier == "Product suitability":

        recommended_action = (
            "Recommend the most suitable product for the shopper"
        )

    elif barrier == "Product quality":

        recommended_action = (
            "Answer the shopper's product quality questions"
        )

    elif barrier == "Returns":

        recommended_action = (
            "Explain the applicable return or exchange policy"
        )

    elif barrier == "Payment":

        recommended_action = (
            "Explain available payment options"
        )

    elif barrier == "Availability":

        recommended_action = (
            "Confirm product availability or expected restock"
        )

    elif intent_level == "High":

        recommended_action = (
            "Follow up with the high-intent shopper"
        )

    elif intent_level == "Medium":

        recommended_action = (
            "Nurture the shopper and provide useful product information"
        )

    else:

        recommended_action = (
            "No immediate action required"
        )

    # ==================================================
    # 7. RECOMMEND TARGETED OFFER
    # ==================================================

    recommended_offer = None

    # Only recommend offers for shoppers
    # who have not already purchased.

    if (
        purchase_status != "Purchased"
        and intent_level == "High"
    ):

        # Price-sensitive shopper
        if barrier == "Price":

            # Cart value >= ₹10,000
            if cart_value >= 10000:

                recommended_offer = {
                    "type": "Fixed discount",
                    "value": 1000,
                    "description": "₹1,000 off on the current cart",
                }

            # Cart value >= ₹7,000
            elif cart_value >= 7000:

                recommended_offer = {
                    "type": "Percentage discount",
                    "value": 10,
                    "description": "10% off, up to ₹1,500",
                }

            # Lower-value cart
            else:

                recommended_offer = {
                    "type": "Percentage discount",
                    "value": 5,
                    "description": "5% off the current cart",
                }

        # Returning high-intent customer
        elif previous_orders >= 2:

            recommended_offer = {
                "type": "Loyalty discount",
                "value": 10,
                "description": "10% loyalty discount, up to ₹1,500",
            }

    # ==================================================
    # 8. RETURN FINAL ANALYSIS
    # ==================================================

    return {
        "intent_score": score,
        "intent_level": intent_level,
        "buying_signals": buying_signals,
        "barrier": barrier,
        "purchase_stage": purchase_stage,
        "urgency": urgency,
        "recommended_action": recommended_action,
        "recommended_offer": recommended_offer,
        "cart_value": cart_value,
        "previous_orders": previous_orders,
        "previous_spend": previous_spend,
        "message": message,
    }

def generate_ai_response(shopper, analysis):
    """
    Generate a personalized customer response using Groq.

    The rule-based analyzer decides the business logic first.
    Groq turns that decision into a natural customer-facing response.
    """

    product_name = shopper.get("product_name", "the product")
    product_price = shopper.get("product_price", "")
    message = shopper.get("message", "")

    intent_level = analysis.get("intent_level", "Low")
    barrier = analysis.get("barrier", "No clear barrier")
    purchase_stage = analysis.get("purchase_stage", "Discovery")
    urgency = analysis.get("urgency", "Normal")
    recommended_action = analysis.get("recommended_action", "")
    recommended_offer = analysis.get("recommended_offer")

    offer_text = "No discount or offer is currently recommended."

    if recommended_offer:
        offer_text = (
            f"{recommended_offer.get('description', '')}"
        )

    prompt = f"""
You are the customer support and sales assistant for an e-commerce brand.

Your job is to write a short, helpful, natural response to the customer.

IMPORTANT:
- Do not invent product facts.
- Do not invent delivery dates.
- Do not invent stock availability.
- Do not invent policies.
- Do not promise anything that is not provided.
- Only mention the discount if an approved offer is provided below.
- Do not mention internal intent scores or internal analysis.
- Do not mention that AI was used.
- Do not pressure the customer.
- Keep the response concise and conversational.

Product:
{product_name}

Product price:
{product_price}

Customer message:
{message}

Internal analysis:
Intent: {intent_level}
Barrier: {barrier}
Purchase stage: {purchase_stage}
Urgency: {urgency}

Recommended business action:
{recommended_action}

Approved offer:
{offer_text}

Write the best customer-facing response.
"""

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful e-commerce customer support "
                    "and sales assistant."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.4,
        max_completion_tokens=300,
        include_reasoning=False,
    )

    return response.choices[0].message.content.strip()