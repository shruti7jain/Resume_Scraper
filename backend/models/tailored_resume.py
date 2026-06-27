"""
Pydantic models for the output of the Resume Optimization Engine.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from backend.models.resume import Resume


class DiffEntry(BaseModel):
    """Represents a single tracked change between the original and tailored resume."""

    field: str = Field(
        ...,
        description="Dot-notation path to the changed field, e.g. 'experience[0].bullets[2]'",
    )
    original: str = Field(..., description="Original text before rewriting")
    updated: str = Field(..., description="Rewritten text after optimization")


class AnalysisReport(BaseModel):
    """Output from the LLM match analysis step."""

    match_score: int = Field(
        ..., ge=0, le=100, description="Resume–JD match score from 0 to 100"
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Skills required by the JD that are absent from the resume",
    )
    experience_gaps: List[str] = Field(
        default_factory=list,
        description="Experience areas in the JD that the resume does not address",
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Actionable suggestions for improving the resume for this role",
    )


class TailoredResume(BaseModel):
    """Complete output of the Resume Shapeshifter optimization pipeline."""

    match_score: int = Field(
        ..., ge=0, le=100, description="Resume–JD match score (0–100)"
    )
    original_resume: Resume = Field(..., description="The original parsed resume")
    tailored_resume: Resume = Field(
        ..., description="The AI-optimized resume with rewritten bullets, summary, and reordered skills"
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Skills in the JD not found in the resume",
    )
    experience_gaps: List[str] = Field(
        default_factory=list,
        description="Experience requirements in the JD the candidate does not satisfy",
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Improvement suggestions from the LLM",
    )
    changes: List[DiffEntry] = Field(
        default_factory=list,
        description="Detailed diff of every change made during optimization",
    )
    session_id: Optional[str] = Field(
        None, description="Unique session identifier for PDF download correlation"
    )
