# API Reference: Resume Shapeshifter Backend

**Base URL (Development):** `http://localhost:8000`  
**Base URL (Production):** `https://your-domain.com`  
**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI)  
**Content Type:** `application/json` (unless noted)

---

## Table of Contents

1. [POST /api/upload-resume](#1-post-apiupload-resume)
2. [POST /api/analyze](#2-post-apianalyze)
3. [POST /api/optimize](#3-post-apioptimize)
4. [POST /api/download-pdf](#4-post-apidownload-pdf)
5. [Data Schemas](#5-data-schemas)
6. [Error Reference](#6-error-reference)

---

## 1. `POST /api/upload-resume`

Upload and parse a resume file (PDF or DOCX) into structured JSON.

### Request

**Content-Type:** `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | `File` | ✅ | Resume file (`.pdf` or `.docx`). Max size: 5MB. |

### Response `200 OK`

```json
{
  "status": "success",
  "resume": {
    "professional_summary": "Results-driven software engineer with 5+ years of experience...",
    "experience": [
      {
        "company": "Acme Corp",
        "role": "Software Engineer",
        "duration": "Jan 2021 – Present",
        "bullets": [
          "Developed RESTful APIs serving 1M+ requests/day",
          "Reduced deployment time by 40% using CI/CD pipelines"
        ]
      }
    ],
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
    "education": [
      {
        "institution": "State University",
        "degree": "B.Tech in Computer Science",
        "year": "2020"
      }
    ],
    "projects": [
      {
        "name": "Inventory Management System",
        "description": "Full-stack app built with React and Django",
        "tech_stack": ["React", "Django", "PostgreSQL"]
      }
    ],
    "certifications": ["AWS Certified Developer – Associate"]
  }
}
```

### Error Responses

| Status | Code | Message |
|---|---|---|
| `400` | `INVALID_FILE_TYPE` | "Only PDF and DOCX files are supported." |
| `413` | `FILE_TOO_LARGE` | "File exceeds the 5MB size limit." |
| `422` | `EMPTY_FILE` | "Uploaded file appears to be empty." |
| `422` | `PROTECTED_PDF` | "PDF is password-protected. Please upload an unlocked version." |
| `422` | `CORRUPT_FILE` | "File could not be read. It may be corrupted." |
| `422` | `SCANNED_PDF` | "Resume appears to be a scanned image. Please upload a text-based PDF." |

### `curl` Example

```bash
curl -X POST http://localhost:8000/api/upload-resume \
  -F "file=@/path/to/my_resume.pdf"
```

---

## 2. `POST /api/analyze`

Sends the parsed resume and job description to the Groq LLM for analysis. Returns a match score, missing skills, experience gaps, and improvement suggestions.

### Request Body

```json
{
  "resume": { ... },        
  "job_description": {
    "raw_text": "We are looking for a Senior Backend Engineer with experience in Python, Kubernetes...",
    "role_title": "Senior Backend Engineer"
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `resume` | `Resume` | ✅ | Parsed resume object from `/api/upload-resume` |
| `job_description.raw_text` | `string` | ✅ | Full raw text of the job description |
| `job_description.role_title` | `string` | No | Optional role title override |

### Response `200 OK`

```json
{
  "status": "success",
  "analysis": {
    "match_score": 72,
    "parsed_jd": {
      "role_title": "Senior Backend Engineer",
      "required_skills": ["Python", "Kubernetes", "PostgreSQL", "REST APIs", "Docker"],
      "preferred_skills": ["Go", "AWS", "Kafka"],
      "responsibilities": [
        "Design and maintain scalable microservices",
        "Collaborate with frontend teams on API contracts"
      ],
      "experience_required": "5+ years",
      "keywords": ["microservices", "distributed systems", "CI/CD", "agile"]
    },
    "missing_skills": ["Kubernetes", "Kafka", "Go"],
    "experience_gaps": [
      "No explicit mention of microservices architecture experience",
      "Leadership or team mentorship not demonstrated"
    ],
    "suggestions": [
      "Emphasize your CI/CD experience in the experience bullets",
      "Reframe the 'Inventory Management' project to highlight distributed system design",
      "Add keywords: 'distributed systems', 'scalable architecture' to your summary"
    ]
  }
}
```

### Error Responses

| Status | Code | Message |
|---|---|---|
| `400` | `EMPTY_JD` | "Job description cannot be empty." |
| `422` | `JD_TOO_SHORT` | "Job description is too short to analyze reliably." |
| `503` | `GROQ_UNAVAILABLE` | "AI service is temporarily unavailable. Please try again." |
| `503` | `GROQ_AUTH_FAILED` | "LLM service authentication failed." |
| `504` | `LLM_TIMEOUT` | "LLM request timed out. Please try again." |

### `curl` Example

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "resume": { "professional_summary": "...", "experience": [...], "skills": [...] },
    "job_description": {
      "raw_text": "We are hiring a Senior Backend Engineer...",
      "role_title": "Senior Backend Engineer"
    }
  }'
```

---

## 3. `POST /api/optimize`

Uses the resume, job description, and analysis report to generate a fully optimized, tailored version of the resume. Tracks every change as a diff.

### Request Body

```json
{
  "resume": { ... },
  "job_description": {
    "raw_text": "We are looking for a Senior Backend Engineer...",
    "role_title": "Senior Backend Engineer"
  },
  "analysis": { ... }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `resume` | `Resume` | ✅ | Original parsed resume |
| `job_description` | `object` | ✅ | Same JD payload as `/api/analyze` |
| `analysis` | `AnalysisReport` | ✅ | Output from `/api/analyze` |

### Response `200 OK`

```json
{
  "status": "success",
  "tailored_resume": {
    "match_score": 72,
    "original_resume": {
      "professional_summary": "Results-driven software engineer with 5+ years...",
      "experience": [ ... ],
      "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
      "education": [ ... ],
      "projects": [ ... ],
      "certifications": [ ... ]
    },
    "optimized_resume": {
      "professional_summary": "Senior backend engineer with 5+ years building scalable, distributed systems...",
      "experience": [
        {
          "company": "Acme Corp",
          "role": "Software Engineer",
          "duration": "Jan 2021 – Present",
          "bullets": [
            "Architected RESTful microservices handling 1M+ requests/day with 99.9% uptime",
            "Streamlined CI/CD pipelines, reducing deployment time by 40% across distributed teams"
          ]
        }
      ],
      "skills": ["Python", "Docker", "PostgreSQL", "FastAPI", "AWS"],
      "education": [ ... ],
      "projects": [ ... ],
      "certifications": [ ... ]
    },
    "missing_skills": ["Kubernetes", "Kafka", "Go"],
    "experience_gaps": [
      "No explicit mention of microservices architecture experience",
      "Leadership or team mentorship not demonstrated"
    ],
    "changes": [
      {
        "field": "professional_summary",
        "original": "Results-driven software engineer with 5+ years...",
        "updated": "Senior backend engineer with 5+ years building scalable, distributed systems..."
      },
      {
        "field": "experience[0].bullets[0]",
        "original": "Developed RESTful APIs serving 1M+ requests/day",
        "updated": "Architected RESTful microservices handling 1M+ requests/day with 99.9% uptime"
      },
      {
        "field": "skills_order",
        "original": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
        "updated": ["Python", "Docker", "PostgreSQL", "FastAPI", "AWS"]
      }
    ]
  }
}
```

### Error Responses

| Status | Code | Message |
|---|---|---|
| `400` | `MISSING_ANALYSIS` | "Analysis report is required to run optimization." |
| `503` | `GROQ_UNAVAILABLE` | "AI service is temporarily unavailable. Please try again." |
| `504` | `LLM_TIMEOUT` | "LLM request timed out. Please try again." |

### `curl` Example

```bash
curl -X POST http://localhost:8000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "resume": { ... },
    "job_description": { "raw_text": "...", "role_title": "Senior Backend Engineer" },
    "analysis": { "match_score": 72, "missing_skills": [...], ... }
  }'
```

---

## 4. `POST /api/download-pdf`

Generates and streams a downloadable PDF containing:
- **Page 1:** Match Score, Missing Skills, Experience Gaps
- **Page 2+:** Side-by-side Original vs Tailored resume with highlighted diffs

### Request Body

```json
{
  "tailored_resume": { ... }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `tailored_resume` | `TailoredResume` | ✅ | Full output object from `/api/optimize` |

### Response `200 OK`

**Content-Type:** `application/pdf`  
**Content-Disposition:** `attachment; filename="tailored_resume.pdf"`

Returns a binary PDF stream.

### Error Responses

| Status | Code | Message |
|---|---|---|
| `400` | `MISSING_TAILORED_RESUME` | "Tailored resume data is required to generate PDF." |
| `503` | `PDF_SERVICE_UNAVAILABLE` | "PDF generation service is unavailable. WeasyPrint may not be installed." |
| `504` | `PDF_TIMEOUT` | "PDF generation timed out. Please try again." |

### `curl` Example

```bash
curl -X POST http://localhost:8000/api/download-pdf \
  -H "Content-Type: application/json" \
  -d '{ "tailored_resume": { ... } }' \
  --output tailored_resume.pdf
```

---

## 5. Data Schemas

### `Resume`

```json
{
  "professional_summary": "string",
  "experience": [
    {
      "company": "string",
      "role": "string",
      "duration": "string",
      "bullets": ["string"]
    }
  ],
  "skills": ["string"],
  "education": [
    {
      "institution": "string",
      "degree": "string",
      "year": "string"
    }
  ],
  "projects": [
    {
      "name": "string",
      "description": "string",
      "tech_stack": ["string"]
    }
  ],
  "certifications": ["string"]
}
```

---

### `JobDescriptionInput`

```json
{
  "raw_text": "string",
  "role_title": "string (optional)"
}
```

---

### `AnalysisReport`

```json
{
  "match_score": "integer (0–100)",
  "parsed_jd": {
    "role_title": "string",
    "required_skills": ["string"],
    "preferred_skills": ["string"],
    "responsibilities": ["string"],
    "experience_required": "string",
    "keywords": ["string"]
  },
  "missing_skills": ["string"],
  "experience_gaps": ["string"],
  "suggestions": ["string"]
}
```

---

### `TailoredResume`

```json
{
  "match_score": "integer (0–100)",
  "original_resume": "Resume",
  "optimized_resume": "Resume",
  "missing_skills": ["string"],
  "experience_gaps": ["string"],
  "changes": [
    {
      "field": "string",
      "original": "string | string[]",
      "updated": "string | string[]"
    }
  ]
}
```

---

### `ChangeEntry`

```json
{
  "field": "string",
  "original": "string or array",
  "updated": "string or array"
}
```

**`field` naming conventions:**

| Value | Meaning |
|---|---|
| `professional_summary` | Summary was rewritten |
| `experience[i].bullets[j]` | Bullet at index `j` of experience entry `i` was rewritten |
| `skills_order` | Skills array was reordered |

---

## 6. Error Reference

All error responses follow this standard structure:

```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "Human-readable description of the error."
}
```

### Full Error Code Table

| HTTP Status | Code | Trigger |
|---|---|---|
| `400` | `INVALID_FILE_TYPE` | Uploaded file is not PDF or DOCX |
| `400` | `EMPTY_JD` | Job description field is blank |
| `400` | `MISSING_ANALYSIS` | `/api/optimize` called without analysis |
| `400` | `MISSING_TAILORED_RESUME` | `/api/download-pdf` called without tailored resume |
| `413` | `FILE_TOO_LARGE` | Uploaded file exceeds 5MB |
| `422` | `EMPTY_FILE` | File has no content |
| `422` | `PROTECTED_PDF` | PDF requires a password |
| `422` | `CORRUPT_FILE` | File bytes are unreadable |
| `422` | `SCANNED_PDF` | PDF contains only images (no text layer) |
| `422` | `JD_TOO_SHORT` | JD text is fewer than ~50 characters |
| `422` | `INVALID_JSON_FROM_LLM` | Groq returned unparseable JSON after retries |
| `503` | `GROQ_UNAVAILABLE` | Groq API is down or unreachable |
| `503` | `GROQ_AUTH_FAILED` | Invalid or expired `GROQ_API_KEY` |
| `503` | `GROQ_RATE_LIMITED` | Groq rate limit hit after retries |
| `503` | `PDF_SERVICE_UNAVAILABLE` | WeasyPrint not installed or failed to initialize |
| `504` | `LLM_TIMEOUT` | Groq did not respond within 30 seconds |
| `504` | `PDF_TIMEOUT` | PDF rendering exceeded 30 seconds |

---

## Call Sequence

The recommended order of API calls for the full user flow:

```
1. POST /api/upload-resume   →  Resume JSON
        │
        ▼
2. POST /api/analyze         →  AnalysisReport (match score, gaps, suggestions)
        │
        ▼
3. POST /api/optimize        →  TailoredResume (optimized resume + diff)
        │
        ▼
4. POST /api/download-pdf    →  PDF binary stream
```

Steps 1–3 must be called in order. Step 4 can be called any time after Step 3 completes.
