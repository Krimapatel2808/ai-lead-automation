import json
import os
import time

from dotenv import load_dotenv
from groq import Groq
from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .database import create_database, save_lead


from .logic import (
    extract_lead_information,
    generate_follow_up,
    calculate_score,
    determine_priority,
    determine_action,
)

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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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