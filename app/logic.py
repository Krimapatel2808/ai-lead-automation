import json
import os
import time

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL = "openai/gpt-oss-20b"

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found. Make sure it is present in your .env file."
    )

client = Groq(api_key=GROQ_API_KEY)


def extract_lead_information(message):

    prompt = f"""
You are an AI sales lead qualification assistant.

Analyze the following customer enquiry and extract structured information.

Customer enquiry:
{message}

Return ONLY valid JSON using exactly this structure:

{{
    "purchase_intent": true,
    "specific_product_or_service": true,
    "quantity_or_scope": true,
    "budget": true,
    "purchase_timeline": true,
    "decision_making_authority": true,
    "requirement": "short summary of the customer's requirement",
    "buying_signals": [
        "signal 1",
        "signal 2"
    ],
    "missing_information": [
        "field_name"
    ]
}}

Rules:

1. Set each boolean to true only when the enquiry clearly provides that information.
2. Do not guess missing information.
3. "purchase_intent" means the customer shows an intention to buy, purchase, subscribe, or implement.
4. "specific_product_or_service" means the customer identifies what they want.
5. "quantity_or_scope" means a quantity, number of users, licenses, locations, project size, etc.
6. "budget" means an explicit budget or spending amount.
7. "purchase_timeline" means an explicit deadline or timeframe.
8. "decision_making_authority" means the person explicitly indicates they can approve or make the purchase decision.
9. "buying_signals" should contain only signals supported by the enquiry.
10. "missing_information" should contain the field names that are not clearly provided.
11. Do not invent information.
12. Return JSON only. No markdown.
"""

    for attempt in range(3):

        try:

            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0,
                response_format={
                    "type": "json_object"
                },
            )

            content = response.choices[0].message.content

            return json.loads(content)


        except Exception as e:

            error_text = str(e)

            if (
                "429" in error_text
                or "rate_limit" in error_text.lower()
                or "503" in error_text
            ):

                if attempt < 2:

                    time.sleep(3)

                    continue

            raise e


# ==================================================
# AI-GENERATED FOLLOW-UP
# ==================================================

def generate_follow_up(
    name,
    company,
    message,
    info,
    score,
    priority,
):

    prompt = f"""
You are an experienced B2B sales representative.

Write a short, professional follow-up email for this lead.

Lead name:
{name}

Company:
{company}

Original customer enquiry:
{message}

Extracted lead information:
{json.dumps(info, ensure_ascii=False)}

Lead score:
{score}

Priority:
{priority}


STRICT RULES:

- Use ONLY facts explicitly present in the original enquiry or extracted information.
- Do not invent pricing, quotes, discounts, features, products, timelines, meetings,
  approvals, commitments, or previous conversations.
- Do not claim that a quote or proposal already exists.
- Do not mention the lead score.
- Do not mention the priority.
- Do not mention AI.
- Do not mention LeadFlow.
- Do not expose internal qualification information.
- Acknowledge the customer's stated requirement.
- Suggest a reasonable next step without assuming that anything has already happened.
- Keep the email concise and natural.
- Do not include a subject line.
- Do not use placeholders such as [Your Name], [Company], [Phone], etc.
- Do not invent the sender's name.
- End with a professional closing.
- Keep the email approximately 80-120 words.

Return ONLY the email text.
"""

    for attempt in range(3):

        try:

            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.3,
            )

            return response.choices[0].message.content.strip()


        except Exception as e:

            error_text = str(e)

            if (
                "429" in error_text
                or "rate_limit" in error_text.lower()
                or "503" in error_text
            ):

                if attempt < 2:

                    time.sleep(3)

                    continue

            raise e


# ==================================================
# DETERMINISTIC LEAD SCORING
# ==================================================

def calculate_score(info):

    score = 0

    scoring_rules = {
        "purchase_intent": 25,
        "specific_product_or_service": 20,
        "quantity_or_scope": 15,
        "budget": 15,
        "purchase_timeline": 15,
        "decision_making_authority": 10,
    }

    for field, points in scoring_rules.items():

        if info.get(field) is True:
            score += points

    return score


# ==================================================
# PRIORITY
# ==================================================

def determine_priority(score):

    if score >= 80:
        return "High"

    elif score >= 50:
        return "Medium"

    else:
        return "Low"


# ==================================================
# RECOMMENDED SALES ACTION
# ==================================================

def determine_action(
    score,
    missing_information,
    message,
):

    message_lower = message.lower()

    information_request = any(
        word in message_lower
        for word in [
            "price",
            "pricing",
            "cost",
            "quote",
            "information",
            "details",
        ]
    )


    if score >= 80:

        return "Notify salesperson immediately"


    elif score >= 50:

        return "Sales follow-up and collect missing information"


    elif information_request:

        return "Send product/pricing information and follow up"


    elif score > 0:

        return "Nurture and collect missing information"


    else:

        return "No immediate sales action"

# ==================================================
# E-COMMERCE SHOPPER ANALYSIS
# ==================================================

def analyze_shopper(shopper):
    """
    Analyze an e-commerce shopper using behavioral,
    customer-history, product, and message signals.
    """

    views = int(shopper.get("product_views", 0))
    added_to_cart = bool(shopper.get("added_to_cart", False))
    checkout_started = bool(shopper.get("checkout_started", False))
    previous_orders = int(shopper.get("previous_orders", 0))
    previous_spend = float(shopper.get("previous_spend", 0))
    cart_value = float(shopper.get("cart_value", 0))
    message = str(shopper.get("message", "")).strip()

    score = 0
    buying_signals = []

    # ==================================================
    # BEHAVIORAL BUYING SIGNALS
    # ==================================================

    # Repeated product interest
    if views >= 5:
        score += 20
        buying_signals.append("Repeated product views")
    elif views >= 3:
        score += 12
        buying_signals.append("Multiple product views")

    # Cart activity
    if added_to_cart:
        score += 25
        buying_signals.append("Added product to cart")

    # Checkout is the strongest behavioral signal
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

    score = min(score, 100)

    # ==================================================
    # INTENT LEVEL
    # ==================================================

    if score >= 75:
        intent_level = "High"
    elif score >= 45:
        intent_level = "Medium"
    else:
        intent_level = "Low"

    # ==================================================
    # PURCHASE BARRIER
    # ==================================================

    message_lower = message.lower()

    if any(word in message_lower for word in [
        "deliver",
        "delivery",
        "reach",
        "arrive",
        "shipping"
    ]):
        barrier = "Delivery"

    elif any(word in message_lower for word in [
        "discount",
        "offer",
        "price",
        "cost",
        "expensive",
        "cheap"
    ]):
        barrier = "Price"

    elif any(word in message_lower for word in [
        "match",
        "shade",
        "color",
        "colour"
    ]):
        barrier = "Color matching"

    elif any(word in message_lower for word in [
        "which",
        "suit",
        "suitable",
        "best for",
        "recommend"
    ]):
        barrier = "Product suitability"

    elif any(word in message_lower for word in [
        "quality",
        "human hair",
        "last",
        "heat",
        "style"
    ]):
        barrier = "Product quality"

    elif any(word in message_lower for word in [
        "return",
        "refund",
        "exchange"
    ]):
        barrier = "Returns"

    elif any(word in message_lower for word in [
        "cod",
        "cash on delivery",
        "upi",
        "payment",
        "emi"
    ]):
        barrier = "Payment"

    elif any(word in message_lower for word in [
        "stock",
        "available",
        "availability"
    ]):
        barrier = "Availability"

    else:
        barrier = "No clear barrier"

    # ==================================================
    # PURCHASE STAGE
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
    # URGENCY
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
        "deadline"
    ]

    urgency = "High" if any(
        word in message_lower for word in urgency_words
    ) else "Normal"

    # ==================================================
    # RECOMMENDED ACTION
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
        recommended_action = "No immediate action required"
    # ==================================================
    # TARGETED OFFER RECOMMENDATION
    # ==================================================

    recommended_offer = None

    purchase_status = str(
        shopper.get("purchase_status", "Not Purchased")
    ).strip()

    if purchase_status != "Purchased" and intent_level == "High":

        if barrier == "Price":

            if cart_value >= 10000:
                recommended_offer = {
                    "type": "Fixed discount",
                    "value": 1000,
                    "description": "₹1,000 off on the current cart",
                }

            elif cart_value >= 7000:
                recommended_offer = {
                    "type": "Percentage discount",
                    "value": 10,
                    "description": "10% off, up to ₹1,500",
                }

            else:
                recommended_offer = {
                    "type": "Percentage discount",
                    "value": 5,
                    "description": "5% off the current cart",
                }

        elif previous_orders >= 2:
            recommended_offer = {
                "type": "Loyalty discount",
                "value": 10,
                "description": "10% loyalty discount, up to ₹1,500",
            }
    # ==================================================
    # FINAL ANALYSIS
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