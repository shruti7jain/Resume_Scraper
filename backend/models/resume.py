"""
Pydantic models for the Resume data structure.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ExperienceEntry(BaseModel):
    company: str = Field(..., description="Name of the company or organisation")
    role: str = Field(..., description="Job title / role at the company")
    duration: str = Field(..., description="Employment period, e.g. 'Jan 2021 – Mar 2023'")
    location: Optional[str] = Field(None, description="City / remote")
    bullets: List[str] = Field(default_factory=list, description="Achievement / responsibility bullets")


class EducationEntry(BaseModel):
    institution: str = Field(..., description="Name of the university or institution")
    degree: str = Field(..., description="Degree type and field, e.g. 'B.Tech in Computer Science'")
    year: str = Field(..., description="Graduation year or period, e.g. '2019 – 2023'")
    gpa: Optional[str] = Field(None, description="GPA or percentage if available")


class ProjectEntry(BaseModel):
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Brief description of the project")
    tech_stack: List[str] = Field(default_factory=list, description="Technologies used")
    link: Optional[str] = Field(None, description="GitHub / live URL")


class Resume(BaseModel):
    """Structured representation of a parsed resume."""

    name: Optional[str] = Field(None, description="Candidate's full name")
    email: Optional[str] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone number")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")

    professional_summary: str = Field(
        default="",
        description="Professional summary or objective statement",
    )
    experience: List[ExperienceEntry] = Field(
        default_factory=list, description="Work experience entries in reverse chronological order"
    )
    skills: List[str] = Field(
        default_factory=list, description="Flat list of skills / technologies"
    )
    education: List[EducationEntry] = Field(
        default_factory=list, description="Education history"
    )
    projects: List[ProjectEntry] = Field(
        default_factory=list, description="Notable projects"
    )
    certifications: List[str] = Field(
        default_factory=list, description="Certifications and online courses"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "professional_summary": "Software engineer with 5 years of experience in backend development.",
                "experience": [
                    {
                        "company": "Acme Corp",
                        "role": "Senior Software Engineer",
                        "duration": "Jan 2021 – Present",
                        "bullets": [
                            "Led migration of monolithic services to microservices, reducing latency by 40%.",
                            "Mentored 3 junior engineers.",
                        ],
                    }
                ],
                "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                "education": [
                    {
                        "institution": "MIT",
                        "degree": "B.Sc. Computer Science",
                        "year": "2019",
                    }
                ],
                "projects": [],
                "certifications": ["AWS Certified Developer – Associate"],
            }
        }
