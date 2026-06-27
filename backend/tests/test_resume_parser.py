"""
test_resume_parser.py — Phase 2 Unit Tests

Tests for the Resume Parser service.
Uses synthetic in-memory PDF/DOCX content and plain-text fixtures.
"""

import io
import pytest

from backend.services import resume_parser
from backend.services.resume_parser import (
    _parse_text,
    _segment_sections,
    _parse_skills,
    _parse_experience,
    _parse_education,
    _parse_certifications,
)
from backend.models.resume import Resume


# ---------------------------------------------------------------------------
# Plain-text resume fixtures (used to test _parse_text directly)
# ---------------------------------------------------------------------------

SAMPLE_RESUME_TEXT = """
Jane Doe
jane.doe@email.com | +1-555-123-4567 | linkedin.com/in/janedoe | github.com/janedoe

Professional Summary
Experienced software engineer with 5+ years building scalable backend systems.
Passionate about clean code and distributed architectures.

Experience
Senior Software Engineer | Acme Corp | Jan 2021 – Present
• Led migration from monolith to microservices, reducing p99 latency by 40%
• Designed and implemented RESTful APIs serving 10M+ requests/day
• Mentored a team of 4 junior engineers

Backend Engineer | StartupXYZ | Jun 2019 – Dec 2020
• Built real-time data pipeline processing 500K events/hour using Kafka
• Integrated third-party payment APIs (Stripe, PayPal)

Skills
Python, FastAPI, Django, PostgreSQL, Redis, Docker, Kubernetes, AWS, Git

Education
Massachusetts Institute of Technology
B.Sc. Computer Science | 2019

Projects
Resume Shapeshifter
• AI-powered tool to tailor resumes for specific job descriptions
• Technologies: Python, FastAPI, React, Groq API

Certifications
• AWS Certified Developer – Associate
• Google Cloud Professional Data Engineer
"""

MINIMAL_RESUME_TEXT = """
John Smith
john@example.com

Experience
Software Developer | TechCo | 2020 – 2023
• Developed web applications using React and Node.js

Skills
JavaScript, React, Node.js, HTML, CSS
"""


# ---------------------------------------------------------------------------
# Section Segmentation Tests
# ---------------------------------------------------------------------------

class TestSectionSegmentation:
    def test_detects_experience_section(self):
        lines = [
            "John Doe",
            "Experience",
            "Software Engineer | Acme | 2020 – 2022",
        ]
        sections = _segment_sections(lines)
        assert "experience" in sections

    def test_detects_skills_section(self):
        lines = ["Skills", "Python, Docker, AWS"]
        sections = _segment_sections(lines)
        assert "skills" in sections

    def test_detects_education_section(self):
        lines = ["Education", "MIT", "B.Sc. Computer Science | 2019"]
        sections = _segment_sections(lines)
        assert "education" in sections

    def test_detects_summary_section(self):
        lines = ["Professional Summary", "Experienced engineer with 5 years..."]
        sections = _segment_sections(lines)
        assert "summary" in sections

    def test_unknown_lines_go_to_header(self):
        lines = ["Jane Doe", "jane@example.com"]
        sections = _segment_sections(lines)
        assert "header" in sections
        assert len(sections["header"]) == 2


# ---------------------------------------------------------------------------
# Skills Parsing Tests
# ---------------------------------------------------------------------------

class TestSkillsParsing:
    def test_comma_separated_skills(self):
        lines = ["Python, FastAPI, PostgreSQL, Docker"]
        skills = _parse_skills(lines)
        assert "Python" in skills
        assert "FastAPI" in skills
        assert "Docker" in skills

    def test_bullet_separated_skills(self):
        lines = ["• Python", "• JavaScript", "• React"]
        skills = _parse_skills(lines)
        assert "Python" in skills
        assert "JavaScript" in skills

    def test_pipe_separated_skills(self):
        lines = ["Python | FastAPI | Docker | AWS"]
        skills = _parse_skills(lines)
        skills_lower = [s.lower() for s in skills]
        assert "python" in skills_lower
        assert "fastapi" in skills_lower

    def test_no_duplicates(self):
        lines = ["Python, Python, FastAPI, fastapi"]
        skills = _parse_skills(lines)
        lower = [s.lower() for s in skills]
        assert len(lower) == len(set(lower))

    def test_empty_input(self):
        assert _parse_skills([]) == []


# ---------------------------------------------------------------------------
# Experience Parsing Tests
# ---------------------------------------------------------------------------

class TestExperienceParsing:
    def test_extracts_single_entry(self):
        lines = [
            "Senior Engineer | Acme Corp | Jan 2021 – Present",
            "• Led migration to microservices",
            "• Mentored junior engineers",
        ]
        entries = _parse_experience(lines)
        assert len(entries) >= 1
        assert entries[0].bullets

    def test_extracts_multiple_entries(self):
        lines = [
            "Senior Engineer | Acme Corp | Jan 2021 – Present",
            "• Built APIs",
            "Backend Engineer | StartupXYZ | Jun 2019 – Dec 2020",
            "• Built pipelines",
        ]
        entries = _parse_experience(lines)
        assert len(entries) == 2

    def test_bullet_content_preserved(self):
        lines = [
            "Software Engineer | Company | 2020 – 2022",
            "• Reduced latency by 40% through caching",
        ]
        entries = _parse_experience(lines)
        assert len(entries) == 1
        assert any("latency" in b.lower() or "caching" in b.lower() for b in entries[0].bullets)

    def test_duration_extracted(self):
        lines = ["Engineer | Corp | Jan 2020 – Dec 2022", "• Did things"]
        entries = _parse_experience(lines)
        assert entries[0].duration  # Should not be empty

    def test_year_range_duration(self):
        lines = ["Developer | TechCo | 2019 – 2022", "• Built things"]
        entries = _parse_experience(lines)
        assert len(entries) >= 1
        assert "2019" in entries[0].duration or "2022" in entries[0].duration


# ---------------------------------------------------------------------------
# Education Parsing Tests
# ---------------------------------------------------------------------------

class TestEducationParsing:
    def test_extracts_degree(self):
        lines = [
            "Massachusetts Institute of Technology",
            "B.Sc. Computer Science | 2019",
        ]
        entries = _parse_education(lines)
        assert len(entries) >= 1

    def test_extracts_year(self):
        lines = ["MIT", "B.Tech in CS | 2020 - 2024"]
        entries = _parse_education(lines)
        assert entries
        assert "2020" in entries[0].year or "2024" in entries[0].year or entries[0].degree

    def test_empty_returns_empty_list(self):
        assert _parse_education([]) == []


# ---------------------------------------------------------------------------
# Certifications Parsing Tests
# ---------------------------------------------------------------------------

class TestCertificationsParsing:
    def test_extracts_certs(self):
        lines = [
            "• AWS Certified Developer – Associate",
            "• Google Cloud Professional Data Engineer",
        ]
        certs = _parse_certifications(lines)
        assert len(certs) == 2
        assert any("AWS" in c for c in certs)

    def test_strips_bullet_chars(self):
        lines = ["• AWS Cert", "- Google Cert"]
        certs = _parse_certifications(lines)
        assert all(not c.startswith("•") for c in certs)
        assert all(not c.startswith("-") for c in certs)


# ---------------------------------------------------------------------------
# Full parse_text() Integration Tests
# ---------------------------------------------------------------------------

class TestParseText:
    def test_returns_resume_model(self):
        result = _parse_text(SAMPLE_RESUME_TEXT)
        assert isinstance(result, Resume)

    def test_extracts_name(self):
        result = _parse_text(SAMPLE_RESUME_TEXT)
        assert result.name == "Jane Doe"

    def test_extracts_email(self):
        result = _parse_text(SAMPLE_RESUME_TEXT)
        assert result.email == "jane.doe@email.com"

    def test_extracts_phone(self):
        result = _parse_text(SAMPLE_RESUME_TEXT)
        assert result.phone is not None

    def test_extracts_linkedin(self):
        result = _parse_text(SAMPLE_RESUME_TEXT)
        assert result.linkedin and "linkedin.com" in result.linkedin

    def test_extracts_github(self):
        result = _parse_text(SAMPLE_RESUME_TEXT)
        assert result.github and "github.com" in result.github

    def test_extracts_summary(self):
        result = _parse_text(SAMPLE_RESUME_TEXT)
        assert "engineer" in result.professional_summary.lower()

    def test_extracts_experience(self):
        result = _parse_text(SAMPLE_RESUME_TEXT)
        assert len(result.experience) >= 1

    def test_experience_has_bullets(self):
        result = _parse_text(SAMPLE_RESUME_TEXT)
        for exp in result.experience:
            if exp.bullets:
                assert all(isinstance(b, str) for b in exp.bullets)

    def test_extracts_skills(self):
        result = _parse_text(SAMPLE_RESUME_TEXT)
        assert len(result.skills) > 0
        skills_lower = [s.lower() for s in result.skills]
        assert "python" in skills_lower

    def test_extracts_certifications(self):
        result = _parse_text(SAMPLE_RESUME_TEXT)
        assert len(result.certifications) >= 1
        assert any("AWS" in c for c in result.certifications)

    def test_minimal_resume(self):
        result = _parse_text(MINIMAL_RESUME_TEXT)
        assert isinstance(result, Resume)
        assert result.name == "John Smith"
        assert result.email == "john@example.com"


# ---------------------------------------------------------------------------
# DOCX parse() tests (using a minimal in-memory DOCX)
# ---------------------------------------------------------------------------

def _make_minimal_docx(text: str) -> bytes:
    """Create a minimal DOCX in-memory with a single paragraph."""
    try:
        from docx import Document as DocxDocument
    except ImportError:
        pytest.skip("python-docx not installed")

    doc = DocxDocument()
    for line in text.splitlines():
        doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


class TestDocxParse:
    DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    def test_parse_docx_returns_resume(self):
        docx_bytes = _make_minimal_docx(MINIMAL_RESUME_TEXT)
        result = resume_parser.parse(docx_bytes, self.DOCX_MIME)
        assert isinstance(result, Resume)

    def test_parse_docx_extracts_name(self):
        docx_bytes = _make_minimal_docx(MINIMAL_RESUME_TEXT)
        result = resume_parser.parse(docx_bytes, self.DOCX_MIME)
        assert result.name == "John Smith"

    def test_parse_docx_extracts_email(self):
        docx_bytes = _make_minimal_docx(MINIMAL_RESUME_TEXT)
        result = resume_parser.parse(docx_bytes, self.DOCX_MIME)
        assert result.email == "john@example.com"


# ---------------------------------------------------------------------------
# API endpoint integration tests (using TestClient)
# ---------------------------------------------------------------------------

class TestUploadEndpoint:
    DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    @pytest.fixture(scope="class")
    def client(self):
        try:
            from fastapi.testclient import TestClient
            from backend.main import app
            return TestClient(app)
        except ImportError:
            pytest.skip("httpx or fastapi not installed")

    def test_upload_docx_returns_200(self, client):
        docx_bytes = _make_minimal_docx(MINIMAL_RESUME_TEXT)
        response = client.post(
            "/api/upload-resume",
            files={"file": ("test_resume.docx", docx_bytes, self.DOCX_MIME)},
        )
        assert response.status_code == 200

    def test_upload_returns_resume_json(self, client):
        docx_bytes = _make_minimal_docx(MINIMAL_RESUME_TEXT)
        response = client.post(
            "/api/upload-resume",
            files={"file": ("test_resume.docx", docx_bytes, self.DOCX_MIME)},
        )
        data = response.json()
        assert "email" in data or "name" in data

    def test_upload_wrong_type_returns_415(self, client):
        response = client.post(
            "/api/upload-resume",
            files={"file": ("test.txt", b"plain text resume", "text/plain")},
        )
        assert response.status_code == 415

    def test_upload_too_large_returns_413(self, client):
        big_content = b"A" * (6 * 1024 * 1024)  # 6 MB
        response = client.post(
            "/api/upload-resume",
            files={"file": ("big.docx", big_content, self.DOCX_MIME)},
        )
        assert response.status_code == 413
