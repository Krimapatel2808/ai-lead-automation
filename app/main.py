import json
import os
import time

from dotenv import load_dotenv
from groq import Groq
from fastapi import FastAPI
from pydantic import BaseModel

from app.database import create_database, save_lead


# ==================================================
# CONFIGURATION
# ==================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL = "openai/gpt-oss-20b"


if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found. Make sure it is present in your .env file."
    )


client = Groq(api_key=GROQ_API_KEY)
app = FastAPI(title="LeadFlow API")



class LeadRequest(BaseModel):
    name: str
    company: str
    message: str


@app.post("/api/leads")
def receive_lead(lead: LeadRequest):

    create_database()

    info = extract_lead_information(lead.message)

    score = calculate_score(info)

    priority = determine_priority(score)

    action = determine_action(
        score,
        info.get("missing_information", []),
        lead.message
    )

    follow_up = generate_follow_up(
        lead.name,
        lead.company,
        lead.message,
        info,
        score,
        priority
    )

    save_lead(
        name=lead.name,
        company=lead.company,
        message=lead.message,
        lead_score=score,
        priority=priority,
        action=action,
        requirement=info.get("requirement", "Not specified")
    )

    return {
        "status": "success",
        "name": lead.name,
        "company": lead.company,
        "lead_score": score,
        "priority": priority,
        "action": action,
        "requirement": info.get("requirement", "Not specified"),
        "follow_up": follow_up
    }


# ==================================================
# AI LEAD INFORMATION EXTRACTION
# ==================================================

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
# CLI APPLICATION
# ==================================================

def main():

    create_database()

    print(
        "AI Lead Qualification System"
    )

    print(
        "----------------------------"
    )


    # ----------------------------------------------
    # INPUT
    # ----------------------------------------------

    name = input(
        "Lead name: "
    ).strip()

    company = input(
        "Company: "
    ).strip()

    message = input(
        "Lead message: "
    ).strip()


    if not name or not company or not message:

        print(
            "\nPlease provide all lead details."
        )

        return


    print(
        "\nAnalyzing lead..."
    )


    # ----------------------------------------------
    # AI EXTRACTION
    # ----------------------------------------------

    info = extract_lead_information(
        message
    )


    # ----------------------------------------------
    # SCORE
    # ----------------------------------------------

    score = calculate_score(
        info
    )


    # ----------------------------------------------
    # PRIORITY
    # ----------------------------------------------

    priority = determine_priority(
        score
    )


    # ----------------------------------------------
    # ACTION
    # ----------------------------------------------

    action = determine_action(
        score,
        info.get(
            "missing_information",
            []
        ),
        message,
    )


    # ----------------------------------------------
    # FOLLOW-UP
    # ----------------------------------------------

    follow_up = generate_follow_up(
        name,
        company,
        message,
        info,
        score,
        priority,
    )


    # ----------------------------------------------
    # SAVE
    # ----------------------------------------------

    save_lead(
        name=name,
        company=company,
        message=message,
        lead_score=score,
        priority=priority,
        action=action,
        requirement=info.get(
            "requirement",
            "Not specified",
        ),
    )


    # ----------------------------------------------
    # OUTPUT
    # ----------------------------------------------

    print(
        "\nAI Lead Analysis"
    )

    print(
        "----------------"
    )

    print(
        f"Lead Score: {score}"
    )

    print(
        f"Priority: {priority}"
    )

    print(
        f"Recommended Action: {action}"
    )

    print(
        f"Requirement: {info.get('requirement', 'Not specified')}"
    )


    print(
        "\nSuggested Follow-up"
    )

    print(
        "-------------------"
    )

    print(
        follow_up
    )


    print(
        "\nLead saved successfully."
    )


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":
    main()