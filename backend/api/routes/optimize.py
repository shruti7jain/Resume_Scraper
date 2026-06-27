"""
POST /api/optimize

Accepts a Resume + JobDescription, runs the full 4-step LLM pipeline,
and returns a complete TailoredResume with diff tracking.

Phase 3: Wired to llm_orchestrator + optimizer
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models.resume import Resume
from backend.models.job_description import JobDescription
from backend.models.tailored_resume import TailoredResume, AnalysisReport
from backend.services import llm_orchestrator, optimizer

logger = logging.getLogger(__name__)
router = APIRouter()


class OptimizeRequest(BaseModel):
    resume: Resume
    job_description: JobDescription
    analysis: AnalysisReport


@router.post("/optimize", response_model=TailoredResume, summary="Generate tailored resume")
async def optimize_resume(request: OptimizeRequest):
    """
    Run the full Resume Optimization Engine (Steps 2–4 of the LLM pipeline):
    - Step 2: Rewrite experience bullets aligned to the JD
    - Step 3: Rewrite professional summary for the target role
    - Step 4: Reorder skills by JD relevance
    - Returns a full TailoredResume with every change tracked as a DiffEntry
    """
    try:
        bullet_rewrites = await llm_orchestrator.rewrite_bullets(
            request.resume, request.job_description, request.analysis
        )
        new_summary = await llm_orchestrator.optimize_summary(
            request.resume, request.job_description, request.analysis
        )
        ranked_skills = await llm_orchestrator.rank_skills(
            request.resume, request.job_description
        )
        result = await optimizer.build_tailored_resume(
            resume=request.resume,
            jd=request.job_description,
            analysis=request.analysis,
            bullet_rewrites=bullet_rewrites,
            new_summary=new_summary,
            ranked_skills=ranked_skills,
        )
    except EnvironmentError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.exception("LLM call failed in /api/optimize")
        raise HTTPException(status_code=502, detail=f"LLM service error: {str(exc)}") from exc
    except Exception as exc:
        logger.exception("Unexpected error in /api/optimize")
        raise HTTPException(status_code=500, detail="Internal server error during optimization.") from exc

    return result
