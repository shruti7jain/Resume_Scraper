"""
POST /api/analyze

Accepts a Resume + JobDescription payload, runs Step 1 of the LLM pipeline
(match analysis via Groq), and returns an AnalysisReport.

Phase 3: Wired to llm_orchestrator.analyze_match()
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models.resume import Resume
from backend.models.job_description import JobDescription
from backend.models.tailored_resume import AnalysisReport
from backend.services import llm_orchestrator

logger = logging.getLogger(__name__)
router = APIRouter()


class AnalyzeRequest(BaseModel):
    resume: Resume
    job_description: JobDescription

    class Config:
        json_schema_extra = {
            "example": {
                "resume": {"name": "Jane Doe", "skills": ["Python", "FastAPI"]},
                "job_description": {"role_title": "Backend Engineer", "required_skills": ["Python"]},
            }
        }


@router.post(
    "/analyze",
    response_model=AnalysisReport,
    summary="Analyze resume against job description",
)
async def analyze(request: AnalyzeRequest):
    """
    Run Step 1 of the LLM pipeline:
    - Compare the parsed resume vs the parsed job description
    - Compute a realistic match score (0–100)
    - Identify missing skills and experience gaps
    - Provide 3–6 actionable improvement suggestions

    Uses Groq LLM (`llama-3.3-70b-versatile` by default).
    Falls back to `mixtral-8x7b-32768` for long context inputs.
    """
    try:
        result = await llm_orchestrator.analyze_match(
            request.resume,
            request.job_description,
        )
    except EnvironmentError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.exception("LLM call failed in /api/analyze")
        raise HTTPException(
            status_code=502,
            detail=f"LLM service error: {str(exc)}",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error in /api/analyze")
        raise HTTPException(status_code=500, detail="Internal server error during analysis.") from exc

    return result
