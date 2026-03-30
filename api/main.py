from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from pipeline.service import run_pipeline_service
from run import get_providers

app = FastAPI(
    title="Parking Matching API",
    version="1.0.0",
    description="API for running parking matching pipeline and retrieving results",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Parking Matching Repository",
        "url": "https://github.com/payamdowlatyari/parking_matching",
    },
)


SUPPORTED_PROVIDERS = ["parkwhiz", "spothero", "cheapairportparking"]


class PipelineRequest(BaseModel):
    airports: List[str]
    start: str
    end: str
    db_path: str = "parking_matching.db"


@app.get("/", tags=["General"])
def root():
    """
    Returns a simple message indicating that the API is functioning correctly.
    """
    return {
        "message": "Parking Matching API",
        "docs": "/docs",
    }


@app.get("/health", tags=["General"])
def health():
    """
    Returns a simple health check for the API.
    """
    return {"status": "ok"}


@app.get("/matches", tags=["General"])
def get_matches():
    """
    Retrieves all stored match results from the database.
    """
    from app.db import Database
    db = Database("parking_matching.db")
    try:
        return db.fetch_all_matches()
    finally:
        db.close()


@app.get("/providers", tags=["General"])
def providers():
    """
    Retrieves a list of supported parking providers.
    """
    return [p.provider_name for p in get_providers()]


@app.post("/pipeline/run", tags=["Pipeline"], response_model=dict)
def run_pipeline(payload: PipelineRequest):
    """
    Runs the full pipeline using the provided parameters.
    """
    if not payload.airports:
        raise HTTPException(status_code=400, detail="At least one airport required")

    result = run_pipeline_service(
        airports=payload.airports,
        start=payload.start,
        end=payload.end,
        db_path=payload.db_path,
    )

    return result