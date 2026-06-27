"""
POST /api/parse-jd

Accepts raw job description text and returns a structured JobDescription JSON.
Phase 2: Wired to jd_parser service.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models.job_description import JobDescription
from backend.services import jd_parser

router = APIRouter()


class ParseJDRequest(BaseModel):
    text: str

    class Config:
        json_schema_extra = {
            "example": {
                "text": (
                    "Software Engineer — Backend\n\n"
                    "We are looking for a Senior Backend Engineer to join our platform team.\n\n"
                    "Responsibilities:\n"
                    "• Design and implement scalable RESTful APIs\n"
                    "• Collaborate with frontend and data teams\n\n"
                    "Requirements:\n"
                    "• 3+ years of experience with Python\n"
                    "• Strong knowledge of FastAPI, PostgreSQL, Docker\n"
                )
            }
        }


@router.post(
    "/parse-jd",
    response_model=JobDescription,
    summary="Parse a raw job description into structured JSON",
)
async def parse_jd(request: ParseJDRequest):
    """
    Accept plain-text job description and return a structured `JobDescription`
    with extracted role title, required/preferred skills, responsibilities,
    experience requirement, and ATS keywords.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=422,
            detail="Job description text cannot be empty.",
        )

    if len(request.text) > 50_000:
        raise HTTPException(
            status_code=413,
            detail="Job description text exceeds the 50,000 character limit.",
        )

    try:
        parsed_jd = jd_parser.parse(request.text.strip())
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to parse job description: {str(exc)}",
        ) from exc

    return parsed_jd
