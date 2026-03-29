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
    openapi_prefix="/api/v1",
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
    return {
        "message": "Parking Matching API",
        "docs": "/docs",
    }


@app.get("/health", tags=["General"])
def health():
    return {"status": "ok"}


@app.get("/matches", tags=["General"])
def get_matches():
    from app.db import Database
    db = Database("parking_matching.db")
    try:
        return db.fetch_all_matches()
    finally:
        db.close()


@app.get("/providers", tags=["General"])
def providers():
    return [p.provider_name for p in get_providers()]


@app.post("/pipeline/run", tags=["Pipeline"])
def run_pipeline(payload: PipelineRequest):
    if not payload.airports:
        raise HTTPException(status_code=400, detail="At least one airport required")

    result = run_pipeline_service(
        airports=payload.airports,
        start=payload.start,
        end=payload.end,
        db_path=payload.db_path,
    )

    return result