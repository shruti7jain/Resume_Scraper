# Architecture: Resume Shapeshifter — AI-Powered Resume Tailoring Engine

## 1. Overview

Resume Shapeshifter is a full-stack AI-powered web application that accepts a user's existing resume and a job description (JD), analyzes the match using **Groq** (ultra-fast LLM inference), and returns an optimized, ATS-friendly version of the resume — truthfully, without fabricating experience.

---

## 2. High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT (Browser)                           │
│                                                                     │
│   ┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐  │
│   │ Resume Upload│    │  JD Input Panel  │    │  Results Panel  │  │
│   │ (PDF / DOCX) │    │  (Paste / Type)  │    │  (Score, Diff,  │  │
│   └──────┬───────┘    └────────┬─────────┘    │   Download PDF) │  │
│          │                    │               └────────▲────────┘  │
└──────────┼────────────────────┼────────────────────────┼───────────┘
           │   REST / HTTP      │                        │
           ▼                    ▼                        │
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKEND API SERVER                           │
│                                                                     │
│   ┌──────────────────┐   ┌──────────────────┐   ┌───────────────┐  │
│   │  Ingestion Layer │   │  JD Parser       │   │  PDF Generator│  │
│   │  (PDF/DOCX Parse)│   │  (NLP Extraction)│   │  (Side-by-Side│  │
│   └──────────┬───────┘   └────────┬─────────┘   └───────▲───────┘  │
│              │                    │                      │          │
│              └──────────┬─────────┘                      │          │
│                         ▼                                │          │
│              ┌───────────────────────┐                   │          │
│              │   LLM Orchestration   │                   │          │
│              │   Layer (Prompt Eng.) │                   │          │
│              └──────────┬────────────┘                   │          │
│                         │                                │          │
│              ┌──────────▼────────────┐                   │          │
│              │  Resume Optimization  │───────────────────┘          │
│              │  Engine               │                              │
│              └───────────────────────┘                              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
              ┌────────────────────────────┐
              │       LLM Provider         │
              │  Groq API                  │
              │  (llama-3.3-70b-versatile) │
              └────────────────────────────┘
```

---

## 3. Layer-by-Layer Breakdown

### 3.1 Frontend (Client Layer)

**Technology:** React.js (Vite) + Vanilla CSS  
**Responsibility:** User interaction, file uploads, displaying results

| Component | Description |
|---|---|
| `ResumeUploader` | Drag-and-drop or browse to upload PDF/DOCX resume |
| `JDInputPanel` | Text area to paste or type the job description |
| `AnalysisResultsPanel` | Displays match score, missing skills, experience gaps |
| `ResumeDiffViewer` | Side-by-side view: Original vs Tailored resume with diff highlights |
| `DownloadButton` | Triggers PDF generation and download of the side-by-side comparison |

**Key UI Flows:**
1. Upload Resume → Preview extracted content
2. Paste JD → Confirm role details
3. Click "Tailor Resume" → Spinner → View results
4. Download PDF

---

### 3.2 Backend API Server

**Technology:** Python (FastAPI) or Node.js (Express)  
**Responsibility:** Orchestrate all processing steps via REST API endpoints

#### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload-resume` | Upload and parse resume (PDF/DOCX) |
| `POST` | `/api/analyze` | Send resume + JD to LLM for analysis |
| `POST` | `/api/optimize` | Generate optimized resume using LLM |
| `GET` | `/api/download-pdf` | Export side-by-side comparison as PDF |

---

### 3.3 Ingestion Layer (Resume Parser)

**Responsibility:** Extract structured data from uploaded resume files

**Libraries:**
- `PyMuPDF` / `pdfplumber` — for PDF text extraction
- `python-docx` — for DOCX parsing
- `spaCy` / regex — for section boundary detection

**Extracted Fields:**

```
Resume {
  professional_summary: string
  experience: [{ company, role, duration, bullets[] }]
  skills: string[]
  education: [{ institution, degree, year }]
  projects: [{ name, description, tech_stack[] }]
  certifications: string[]
}
```

---

### 3.4 JD Parser

**Responsibility:** Extract structured requirements from the raw job description text

**Extracted Fields:**

```
JobDescription {
  role_title: string
  company: string (optional)
  required_skills: string[]
  preferred_skills: string[]
  responsibilities: string[]
  experience_required: string
  keywords: string[]
}
```

**Approach:** Regex + LLM-assisted extraction for nuanced requirements.

---

### 3.5 LLM Orchestration Layer (Prompt Engineering)

**Responsibility:** Construct structured prompts, manage LLM calls, parse responses

**LLM Provider: Groq**

Groq is used for all inference due to its industry-leading speed (low latency, high tokens/sec), making the tailoring experience feel near-instant.

| Model | Use Case |
|---|---|
| `llama-3.3-70b-versatile` | Primary model — match analysis, bullet rewriting, summary optimization |
| `mixtral-8x7b-32768` | Fallback / long-context tasks (large resumes or JDs) |

**Integration:** `groq` Python SDK (`pip install groq`)

```python
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"},
)
```

**Prompt Strategies:**

| Task | Prompt Type | Output Format |
|---|---|---|
| Resume–JD Match Analysis | Structured comparison prompt | JSON: `{ match_score, missing_skills, experience_gaps, suggestions }` |
| Bullet Rewriting | Few-shot rewriting prompt | JSON: `{ original_bullet, rewritten_bullet }[]` |
| Skills Reordering | Ranking prompt | JSON: `{ ranked_skills[] }` |
| Summary Optimization | Instruction prompt | `string` (new summary) |

**Prompt Chaining Flow:**
```
Step 1: analyze_resume_jd_match(resume, jd)  →  analysis_report
Step 2: rewrite_bullets(resume.experience, jd, analysis_report)  →  new_bullets
Step 3: optimize_summary(resume.summary, jd)  →  new_summary
Step 4: reorder_skills(resume.skills, jd.required_skills)  →  ranked_skills
Step 5: assemble_optimized_resume(...)  →  tailored_resume
```

---

### 3.6 Resume Optimization Engine

**Responsibility:** Assemble the final tailored resume from LLM outputs

**Rules enforced:**
- No fabricated experience or companies
- Only rewords/restructures existing content
- Preserves all original dates, roles, and institutions
- Injects JD keywords naturally into existing bullets
- Flags changes for transparency (diff tracking)

**Output Object:**

```
TailoredResume {
  match_score: number          // 0–100
  original_resume: Resume
  tailored_resume: Resume
  missing_skills: string[]
  experience_gaps: string[]
  changes: [{ field, original, updated }]
}
```

---

### 3.7 PDF Generation Service

**Responsibility:** Render and export a downloadable side-by-side comparison PDF

**Library:** `WeasyPrint` (Python) or `Puppeteer` (Node.js)

**PDF Layout:**
- Page 1: Match Score Summary + Missing Skills + Gaps
- Page 2+: Side-by-side Original vs Tailored resume with highlighted diffs

---

## 4. Data Flow

```
User Uploads Resume (PDF/DOCX)
        │
        ▼
[Ingestion Layer] ── extracts ──► Structured Resume JSON
        │
        │   User Pastes JD
        │          │
        ▼          ▼
[JD Parser] ── extracts ──► Structured JD JSON
        │
        ▼
[LLM Orchestration Layer]
   ├── Match Analysis     ──► match_score, missing_skills, gaps
   ├── Bullet Rewriting   ──► improved_bullets[]
   ├── Summary Rewrite    ──► new_summary
   └── Skills Reordering  ──► ranked_skills[]
        │
        ▼
[Optimization Engine] ── assembles ──► TailoredResume
        │
        ├──► REST Response to Frontend (JSON)
        │       └── ResultsPanel renders Score, Diffs, Skills
        │
        └──► PDF Generator ──► Downloadable PDF
```

---

## 5. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React.js + Vite | SPA, component-based UI |
| **Styling** | Vanilla CSS | Custom design system |
| **Backend** | FastAPI (Python) | REST API server |
| **Resume Parsing** | pdfplumber, python-docx | Extract resume content |
| **LLM Integration** | Groq API (llama-3.3-70b-versatile) | Ultra-fast AI analysis & rewriting |
| **Prompt Management** | Custom prompt builder + `groq` SDK | Prompt chaining, JSON output parsing |
| **PDF Export** | WeasyPrint / Puppeteer | Side-by-side PDF generation |
| **Storage** | In-memory / temp files | Resume file handling (session-scoped) |
| **Environment** | `.env` config | API keys, model selection |

---

## 6. Folder Structure

```
resume-shapeshifter/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ResumeUploader.jsx
│   │   │   ├── JDInputPanel.jsx
│   │   │   ├── AnalysisResultsPanel.jsx
│   │   │   ├── ResumeDiffViewer.jsx
│   │   │   └── DownloadButton.jsx
│   │   ├── pages/
│   │   │   └── Home.jsx
│   │   ├── App.jsx
│   │   └── index.css
│   └── index.html
│
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── upload.py        # /api/upload-resume
│   │   │   ├── analyze.py       # /api/analyze
│   │   │   ├── optimize.py      # /api/optimize
│   │   │   └── download.py      # /api/download-pdf
│   ├── services/
│   │   ├── resume_parser.py     # Ingestion Layer
│   │   ├── jd_parser.py         # JD Parser
│   │   ├── llm_orchestrator.py  # LLM Orchestration Layer
│   │   ├── optimizer.py         # Resume Optimization Engine
│   │   └── pdf_generator.py     # PDF Generation Service
│   ├── prompts/
│   │   ├── match_analysis.txt
│   │   ├── bullet_rewrite.txt
│   │   ├── summary_optimize.txt
│   │   └── skill_rank.txt
│   ├── models/
│   │   ├── resume.py            # Pydantic models
│   │   └── job_description.py
│   └── main.py                  # FastAPI app entry point
│
├── docs/
│   ├── context.md
│   ├── architecture.md
│   └── problemstatement.txt
│
├── .env.example
├── requirements.txt
└── README.md
```

---

## 7. Key Design Decisions

| Decision | Rationale |
|---|---|
| **No database** | All processing is session-scoped; no PII stored persistently |
| **Prompt chaining** | Breaks complex LLM task into discrete, testable steps |
| **JSON-structured LLM outputs** | Enables reliable parsing and diff tracking |
| **Groq as LLM provider** | Ultra-low latency inference; supports llama-3.3-70b and mixtral-8x7b |
| **Facts-only optimization** | Ensures ethical use — no hallucinated experience added |
| **Diff tracking in output** | Transparency for the user — every change is visible |

---

## 8. Security Considerations

- **No persistent resume storage** — files are processed in-memory and discarded after the session
- **API key protection** — `GROQ_API_KEY` stored only in `.env`, never exposed to frontend
- **Input validation** — file type and size limits enforced on upload
- **Rate limiting** — backend endpoints rate-limited to prevent abuse
- **CORS** — strict origin whitelisting in production

---

## 9. Post-Phase 5 / Production Architecture

After Phase 5, the application transitions from a development setup to a proper production-ready deployment. 

**Frontend (Production Build):**
- The React (Vite) application is built into static assets (HTML/CSS/JS) located in `frontend/dist/`.
- These static assets can be served via a lightweight web server like Nginx, or directly hosted on a CDN (e.g., Vercel, Netlify, or AWS CloudFront) for high availability.

**Backend (Production Deployment):**
- The FastAPI application is run using a production ASGI server like `Uvicorn` managed by `Gunicorn` (e.g., `gunicorn -k uvicorn.workers.UvicornWorker main:app`) to handle concurrent requests efficiently.
- Deployed behind a reverse proxy (like Nginx) which handles SSL termination (HTTPS) and routes `/api/*` traffic to the backend server.

**Continuous Integration / Continuous Deployment (CI/CD):**
- **Testing:** Automated tests run for parser logic (pytest) and React components (Vitest/Playwright).
- **Dockerization:** Both frontend and backend are containerized (`Dockerfile` and `docker-compose.yml`) to ensure consistency across environments.

---

## 10. Scalability & Future Enhancements

| Feature | Priority | Notes |
|---|---|---|
| User accounts & history | Medium | Save past tailored resumes |
| Multiple JD comparison | Medium | Compare resume against several roles |
| LinkedIn import | Low | OAuth-based profile import |
| Cover letter generation | Medium | Extend LLM pipeline to generate cover letter |
| ATS simulation scoring | High | Simulate ATS parsing to validate keyword alignment |
| Multi-language support | Low | Handle resumes in languages other than English |
| Batch processing | Low | Upload multiple JDs and get ranked tailoring |
