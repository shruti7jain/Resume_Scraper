from backend.services.optimizer import build_tailored_resume, _generate_diff
from backend.models.resume import Resume, ExperienceEntry
from backend.models.job_description import JobDescription
from backend.models.tailored_resume import AnalysisReport

def test_generate_diff():
    original = "Developed new feature"
    updated = "Developed new feature in React"
    
    diff = _generate_diff("experience[0].bullets[0]", original, updated)
    assert diff is not None
    assert diff.field == "experience[0].bullets[0]"
    assert diff.original == original
    assert diff.updated == updated

    # Test no diff if same
    assert _generate_diff("field", "Same", "Same") is None

def test_build_tailored_resume():
    original_resume = Resume(
        name="John",
        professional_summary="Old summary",
        experience=[ExperienceEntry(company="A", role="B", duration="2020", bullets=["Did X", "Did Y"])],
        skills=["Python", "C++"],
        education=[],
        projects=[],
        certifications=[]
    )
    
    jd = JobDescription(
        role_title="Dev", required_skills=[], preferred_skills=[], responsibilities=[], experience_required="", keywords=[]
    )
    
    analysis = AnalysisReport(match_score=80, missing_skills=[], experience_gaps=[], suggestions=[])
    
    llm_outputs = {
        "analysis_report": analysis,
        "improved_bullets": [{"original": "Did X", "improved": "Did X with Python"}],
        "new_summary": "New summary",
        "ranked_skills": ["C++", "Python"]
    }
    
    tailored = build_tailored_resume(original_resume, jd, llm_outputs)
    
    assert tailored.match_score == 80
    assert tailored.tailored_resume.professional_summary == "New summary"
    assert tailored.tailored_resume.skills == ["C++", "Python"]
    assert tailored.tailored_resume.experience[0].bullets[0] == "Did X with Python"
    assert tailored.tailored_resume.experience[0].bullets[1] == "Did Y" # Unchanged
    
    assert len(tailored.changes) == 3 # summary, skills, 1 bullet
