from __future__ import annotations

import logging
import os

from fastapi import FastAPI, Header, HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from pydantic import BaseModel, Field

from .sheet_service import append_submission, worksheet


logger = logging.getLogger(__name__)
app = FastAPI(title="Info Sheet API", version="1.0.0")


class Submission(BaseModel):
    your_name: str = Field(min_length=1, max_length=100)
    are_you_a_cat: str = Field(min_length=1, max_length=100)
    makes_biscuits: str = Field(min_length=1, max_length=100)
    can_purr: str = Field(min_length=1, max_length=100)


class SubmissionResult(BaseModel):
    success: bool
    row: int


def authorize_google_user(authorization: str | None) -> dict[str, object]:
    client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "").strip()
    if not client_id:
        raise RuntimeError("GOOGLE_OAUTH_CLIENT_ID is not configured")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Google sign-in is required")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        identity = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            client_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=401, detail="Invalid Google identity token") from error
    if not identity.get("email_verified"):
        raise HTTPException(status_code=401, detail="Google email is not verified")
    return identity


@app.get("/health")
def health() -> dict[str, str]:
    try:
        worksheet().row_values(1)
    except Exception as error:
        logger.exception("Google Sheets health check failed")
        raise HTTPException(status_code=503, detail="Google Sheets is unavailable") from error
    return {"status": "ok"}


@app.post("/submissions", response_model=SubmissionResult, status_code=201)
def create_submission(
    submission: Submission,
    authorization: str | None = Header(default=None),
) -> SubmissionResult:
    authorize_google_user(authorization)
    try:
        row = append_submission(
            your_name=submission.your_name,
            are_you_a_cat=submission.are_you_a_cat,
            makes_biscuits=submission.makes_biscuits,
            can_purr=submission.can_purr,
        )
    except Exception as error:
        logger.exception("Failed to append a Google Sheets row")
        raise HTTPException(status_code=502, detail="Failed to write to Google Sheets") from error
    return SubmissionResult(success=True, row=row)
