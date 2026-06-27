import requests

def test_api():
    print("Testing /api/parse-jd...")
    try:
        jd_res = requests.post("http://localhost:8000/api/parse-jd", json={"text": "Software Engineer with Python experience"})
        print("Parse JD Status:", jd_res.status_code)
        if jd_res.status_code != 200:
            print("Parse JD Error:", jd_res.text)
            return
            
        print("Parse JD Success:", jd_res.json())
        
        # Now test analysis
        print("\nTesting /api/analyze (using fake resume)...")
        resume = {
            "name": "Test User",
            "email": "test@test.com",
            "phone": "123",
            "linkedin": None,
            "github": None,
            "professional_summary": "Test",
            "experience": [],
            "skills": ["Python"],
            "education": [],
            "projects": [],
            "certifications": []
        }
        
        analyze_res = requests.post("http://localhost:8000/api/analyze", json={
            "resume": resume,
            "job_description": jd_res.json()
        })
        
        print("Analyze Status:", analyze_res.status_code)
        if analyze_res.status_code != 200:
            print("Analyze Error:", analyze_res.text)
        else:
            print("Analyze Success!")
            
    except Exception as e:
        print("Connection failed:", e)

if __name__ == "__main__":
    test_api()
