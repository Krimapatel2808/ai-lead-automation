import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.logic import analyze_shopper, generate_ai_response


app = FastAPI(
    title="LeadFlow API",
    description="AI-assisted revenue recovery API for e-commerce businesses.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATA_FILE = "data/leadflow_analyzed.csv"


@app.get("/")
def root():
    return {
        "status": "success",
        "message": "LeadFlow API is running",
    }


@app.get("/api/opportunities")
def get_opportunities():
    try:
        df = pd.read_csv(DATA_FILE)

        return {
            "status": "success",
            "count": len(df),
            "opportunities": (
                df.astype(object)
                .where(pd.notna(df), None)
                .to_dict(orient="records")
            ),
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Data file not found: {DATA_FILE}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@app.post("/api/generate-response")
def generate_response(shopper: dict):
    try:
        analysis = analyze_shopper(shopper)

        ai_response = generate_ai_response(
            shopper,
            analysis,
        )

        return {
            "status": "success",
            "analysis": analysis,
            "ai_response": ai_response,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )