import sqlite3

DATABASE_NAME = "leads.db"


DEMO_LEADS = [
    (
        "Priya Sharma",
        "Acme Technologies",
        "We want to purchase 200 enterprise licenses. "
        "Our budget is ₹10 lakh and we need implementation before October 15. "
        "I am the procurement manager and can approve the purchase.",
        100,
        "High",
        "Notify salesperson immediately",
        "Purchase 200 enterprise licenses with ₹10 lakh budget, "
        "implementation before October 15, procurement manager approval.",
    ),
    (
        "Rahul Mehta",
        "Nova Retail",
        "We need around 500 units of your product. "
        "Our budget is approximately ₹5 lakh and we would like to purchase "
        "this month. Please connect me with your sales team.",
        70,
        "Medium",
        "Sales follow-up and collect missing information",
        "Purchase of approximately 500 units with ₹5 lakh budget "
        "and purchase planned this month.",
    ),
    (
        "Ananya Kapoor",
        "BrightWorks Studio",
        "Can you send me your product brochure and pricing? "
        "We are evaluating a few options for our team.",
        0,
        "Low",
        "Send product/pricing information and follow up",
        "Evaluating product options and requesting product/pricing information.",
    ),
    (
        "Vikram Singh",
        "Vertex Logistics",
        "We are looking for an automated customer support solution "
        "for our operations team. We may need it for approximately "
        "50 users. Please share more details.",
        40,
        "Low",
        "Nurture and collect missing information",
        "Automated customer support solution for approximately 50 users.",
    ),
    (
        "Neha Patel",
        "FinEdge Solutions",
        "We are planning to implement an AI lead management system "
        "for our sales team of 30 people. Our estimated budget is "
        "₹8 lakh and we want to start the project next quarter. "
        "I am leading the evaluation and will be involved in the final decision.",
        100,
        "High",
        "Notify salesperson immediately",
        "AI lead management system for a 30-person sales team, "
        "₹8 lakh estimated budget, implementation next quarter, "
        "evaluation led by the contact.",
    ),
    (
        "Arjun Malhotra",
        "UrbanCart",
        "We are interested in your automation solution. "
        "Could someone explain how it works and what the typical "
        "implementation process looks like?",
        25,
        "Low",
        "Nurture and collect missing information",
        "Interested in automation solution; requesting implementation details.",
    ),
]


def seed_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM leads")

    cursor.executemany(
        """
        INSERT INTO leads (
            name,
            company,
            message,
            lead_score,
            priority,
            action,
            requirement
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        DEMO_LEADS,
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    seed_database()

    print("Demo database reset successfully.")
    print(f"Inserted {len(DEMO_LEADS)} synthetic leads.")
    