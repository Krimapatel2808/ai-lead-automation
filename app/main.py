import json
import os
import time
import sqlite3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.database import create_database, save_lead
from app.logic import (
    extract_lead_information,
    calculate_score,
    determine_priority,
    determine_action,
    generate_follow_up,
)

app = FastAPI(title="LeadFlow API")


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Existing website enquiry model
# --------------------------------------------------

class LeadRequest(BaseModel):
    name: str
    company: str
    message: str


# --------------------------------------------------
# Existing lead intake endpoint
# --------------------------------------------------

@app.post("/api/leads")
def create_lead(lead: LeadRequest):

    create_database()

    information = extract_lead_information(lead.message)

    score = calculate_score(information)

    priority = determine_priority(score)

    action = determine_action(
        score,
        information.get("missing_information", []),
        lead.message,
    )

    follow_up = generate_follow_up(
        lead.name,
        lead.company,
        lead.message,
        information,
        action,
    )

    save_lead(
        lead.name,
        lead.company,
        lead.message,
        score,
        priority,
        action,
        information.get("requirement"),
    )

    return {
        "status": "success",
        "name": lead.name,
        "company": lead.company,
        "score": score,
        "priority": priority,
        "action": action,
        "requirement": information.get("requirement"),
        "follow_up": follow_up,
    }


# --------------------------------------------------
# Existing leads endpoint
# --------------------------------------------------

@app.get("/api/leads")
def get_leads():

    create_database()

    connection = sqlite3.connect("leads.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
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
    """)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# --------------------------------------------------
# E-commerce opportunity endpoint
# --------------------------------------------------

@app.get("/api/opportunities")
def get_opportunities():

    import pandas as pd

    file_path = "data/leadflow_analyzed.csv"

    if not os.path.exists(file_path):
        return {
            "status": "error",
            "message": "Analyzed dataset not found.",
        }

    df = pd.read_csv(file_path)

    # Convert NaN values to empty strings
    df = df.fillna("")

    return {
        "status": "success",
        "count": len(df),
        "opportunities": df.to_dict(orient="records"),
    }


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "LeadFlow API",
    }


# --------------------------------------------------
# Local development
# --------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )