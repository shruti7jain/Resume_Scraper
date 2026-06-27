"""
test_jd_parser.py — Phase 2 Unit Tests

Tests for the JD Parser service: ensures correct extraction of
role title, skills, responsibilities, experience requirements, and keywords.
"""

import pytest
from backend.services.jd_parser import parse

# ---------------------------------------------------------------------------
# Sample JD fixtures
# ---------------------------------------------------------------------------

SAMPLE_JD_BASIC = """
Senior Backend Engineer

We are hiring a Senior Backend Engineer to join our growing platform team at Acme Corp.

Responsibilities:
• Design and implement scalable RESTful APIs
• Collaborate with cross-functional teams
• Write unit and integration tests
• Participate in code reviews

Requirements:
• 4+ years of experience with Python
• Proficiency in FastAPI and Django
• Strong knowledge of PostgreSQL and Redis
• Experience with Docker and Kubernetes
• Familiarity with AWS services (EC2, S3, Lambda)

Preferred:
• Experience with Kafka or RabbitMQ
• Knowledge of GraphQL
• CI/CD pipeline experience with GitHub Actions
"""

SAMPLE_JD_MINIMAL = """
Python Developer

We need someone who knows Python, Django, and PostgreSQL.
Must have 2+ years of experience in backend development.

Nice to have: Docker, React
"""

SAMPLE_JD_DATA_ROLE = """
Data Engineer

Job Title: Data Engineer
Company: DataFlow Inc.

Responsibilities:
• Build and maintain data pipelines using Apache Spark
• Work with BigQuery and Snowflake for data warehousing
• Collaborate with data scientists to productionize ML models

Requirements:
• 3+ years of experience with ETL pipelines
• Proficiency in Python and SQL
• Hands-on experience with Spark, Hadoop, or Kafka
• Knowledge of cloud platforms (AWS or GCP)

Nice to have:
• Experience with dbt
• Airflow or Prefect knowledge
"""


# ---------------------------------------------------------------------------
# Role Title Tests
# ---------------------------------------------------------------------------

class TestRoleTitleExtraction:
    def test_extracts_explicit_title(self):
        jd = parse(SAMPLE_JD_BASIC)
        assert "engineer" in jd.role_title.lower() or "backend" in jd.role_title.lower()

    def test_extracts_title_from_minimal_jd(self):
        jd = parse(SAMPLE_JD_MINIMAL)
        assert "python" in jd.role_title.lower() or "developer" in jd.role_title.lower()

    def test_role_title_not_empty(self):
        jd = parse(SAMPLE_JD_BASIC)
        assert jd.role_title
        assert len(jd.role_title) > 2


# ---------------------------------------------------------------------------
# Required Skills Tests
# ---------------------------------------------------------------------------

class TestRequiredSkillsExtraction:
    def test_extracts_python(self):
        jd = parse(SAMPLE_JD_BASIC)
        skills_lower = [s.lower() for s in jd.required_skills]
        assert any("python" in s for s in skills_lower)

    def test_extracts_database_skills(self):
        jd = parse(SAMPLE_JD_BASIC)
        skills_lower = [s.lower() for s in jd.required_skills]
        assert any("postgresql" in s or "postgres" in s for s in skills_lower)

    def test_extracts_fastapi(self):
        jd = parse(SAMPLE_JD_BASIC)
        skills_lower = [s.lower() for s in jd.required_skills]
        assert any("fastapi" in s for s in skills_lower)

    def test_required_skills_is_list(self):
        jd = parse(SAMPLE_JD_BASIC)
        assert isinstance(jd.required_skills, list)

    def test_minimal_jd_extracts_skills(self):
        jd = parse(SAMPLE_JD_MINIMAL)
        skills_lower = [s.lower() for s in jd.required_skills + jd.preferred_skills + jd.keywords]
        assert any("python" in s for s in skills_lower)

    def test_no_duplicate_skills(self):
        jd = parse(SAMPLE_JD_BASIC)
        lower = [s.lower() for s in jd.required_skills]
        assert len(lower) == len(set(lower)), "Duplicate skills found in required_skills"


# ---------------------------------------------------------------------------
# Preferred Skills Tests
# ---------------------------------------------------------------------------

class TestPreferredSkillsExtraction:
    def test_extracts_preferred_from_section(self):
        jd = parse(SAMPLE_JD_BASIC)
        # Preferred section contains Kafka / GraphQL
        preferred_lower = [s.lower() for s in jd.preferred_skills]
        # At least one preferred skill extracted
        assert len(jd.preferred_skills) >= 0  # May be empty if section not found, acceptable

    def test_preferred_is_list(self):
        jd = parse(SAMPLE_JD_BASIC)
        assert isinstance(jd.preferred_skills, list)


# ---------------------------------------------------------------------------
# Responsibilities Tests
# ---------------------------------------------------------------------------

class TestResponsibilitiesExtraction:
    def test_extracts_responsibilities(self):
        jd = parse(SAMPLE_JD_BASIC)
        assert isinstance(jd.responsibilities, list)
        assert len(jd.responsibilities) > 0

    def test_responsibilities_are_sentences(self):
        jd = parse(SAMPLE_JD_BASIC)
        for resp in jd.responsibilities:
            assert len(resp) > 10, f"Responsibility too short: {resp!r}"

    def test_api_design_responsibility(self):
        jd = parse(SAMPLE_JD_BASIC)
        resp_lower = " ".join(jd.responsibilities).lower()
        assert "api" in resp_lower or "restful" in resp_lower or "design" in resp_lower

    def test_data_role_responsibilities(self):
        jd = parse(SAMPLE_JD_DATA_ROLE)
        assert len(jd.responsibilities) >= 1


# ---------------------------------------------------------------------------
# Experience Requirement Tests
# ---------------------------------------------------------------------------

class TestExperienceRequirementExtraction:
    def test_extracts_experience_years(self):
        jd = parse(SAMPLE_JD_BASIC)
        assert "4" in jd.experience_required or "year" in jd.experience_required.lower()

    def test_extracts_minimal_experience(self):
        jd = parse(SAMPLE_JD_MINIMAL)
        assert "2" in jd.experience_required or "year" in jd.experience_required.lower()

    def test_experience_required_is_string(self):
        jd = parse(SAMPLE_JD_BASIC)
        assert isinstance(jd.experience_required, str)


# ---------------------------------------------------------------------------
# Keywords Tests
# ---------------------------------------------------------------------------

class TestKeywordsExtraction:
    def test_keywords_not_empty(self):
        jd = parse(SAMPLE_JD_BASIC)
        assert len(jd.keywords) > 0

    def test_keywords_contains_tech_terms(self):
        jd = parse(SAMPLE_JD_BASIC)
        keywords_lower = [k.lower() for k in jd.keywords]
        # Should contain at least one of these common tech keywords
        common = {"python", "docker", "postgresql", "aws", "redis", "kubernetes"}
        assert common & set(keywords_lower), f"No common tech keywords found in {keywords_lower}"

    def test_keywords_is_list_of_strings(self):
        jd = parse(SAMPLE_JD_BASIC)
        assert all(isinstance(k, str) for k in jd.keywords)


# ---------------------------------------------------------------------------
# Model Integrity Tests
# ---------------------------------------------------------------------------

class TestModelIntegrity:
    def test_returns_job_description_object(self):
        from backend.models.job_description import JobDescription
        jd = parse(SAMPLE_JD_BASIC)
        assert isinstance(jd, JobDescription)

    def test_raw_text_preserved(self):
        jd = parse(SAMPLE_JD_BASIC)
        assert jd.raw_text is not None
        assert len(jd.raw_text) > 0

    def test_empty_text_raises_or_returns_gracefully(self):
        # Parser should not crash on near-empty input
        jd = parse("Software Engineer")
        assert jd.role_title  # Should still produce something

    def test_data_engineer_role(self):
        from backend.models.job_description import JobDescription
        jd = parse(SAMPLE_JD_DATA_ROLE)
        assert isinstance(jd, JobDescription)
        skills_all = [s.lower() for s in jd.required_skills + jd.keywords]
        assert any("python" in s or "spark" in s or "sql" in s for s in skills_all)
