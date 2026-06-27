from backend.models.tailored_resume import TailoredResume
from backend.services.pdf_generator import generate

mock_data = {
    "match_score": 85,
    "missing_skills": ["Docker", "Kubernetes"],
    "experience_gaps": ["No production Kubernetes experience"],
    "suggestions": ["Add Docker to summary"],
    "original_resume": {
        "professional_summary": "Software Engineer",
        "experience": [],
        "skills": ["Python"],
        "education": [],
        "projects": [],
        "certifications": []
    },
    "tailored_resume": {
        "professional_summary": "Software Engineer with Docker",
        "experience": [],
        "skills": ["Python", "Docker"],
        "education": [],
        "projects": [],
        "certifications": []
    }
}

try:
    resume = TailoredResume(**mock_data)
    pdf = generate(resume)
    print("SUCCESS, bytes generated:", len(pdf))
except Exception as e:
    import traceback
    traceback.print_exc()
