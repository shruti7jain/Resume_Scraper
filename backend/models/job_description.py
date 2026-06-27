"""
Pydantic models for Job Description data structure.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class JobDescription(BaseModel):
    """Structured representation of a parsed job description."""

    role_title: str = Field(..., description="Job title being applied for")
    company: Optional[str] = Field(None, description="Company name if mentioned in JD")
    required_skills: List[str] = Field(
        default_factory=list,
        description="Mandatory technical skills listed in the JD",
    )
    preferred_skills: List[str] = Field(
        default_factory=list,
        description="Nice-to-have or preferred skills listed in the JD",
    )
    responsibilities: List[str] = Field(
        default_factory=list,
        description="Key responsibilities / duties in the role",
    )
    experience_required: str = Field(
        default="",
        description="Experience requirement string, e.g. '3+ years of Python development'",
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="ATS-relevant keywords extracted from the JD",
    )
    raw_text: Optional[str] = Field(
        None,
        description="Original raw text of the job description (used for LLM prompting)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "role_title": "Backend Engineer",
                "company": "Acme Corp",
                "required_skills": ["Python", "FastAPI", "PostgreSQL"],
                "preferred_skills": ["Docker", "Kubernetes", "Redis"],
                "responsibilities": [
                    "Design and implement RESTful APIs",
                    "Collaborate with cross-functional teams",
                ],
                "experience_required": "3+ years",
                "keywords": ["microservices", "CI/CD", "agile"],
            }
        }
