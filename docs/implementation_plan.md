# Implementation Plan: Resume Shapeshifter
## AI-Powered Resume Tailoring Engine

> **Stack:** React (Vite) + FastAPI (Python) + Groq API  
> **Total Phases:** 5  
> **Estimated Duration:** ~3–4 weeks

---

## Phase Overview

| Phase | Name | Focus | Est. Duration |
|---|---|---|---|
| **Phase 1** | Project Scaffolding & Setup | Repo, env, folder structure, base configs | 1–2 days |
| **Phase 2** | Backend Core — Ingestion & Parsing | Resume parser, JD parser, API endpoints | 4–5 days |
| **Phase 3** | LLM Integration — Groq Orchestration | Prompt engineering, match analysis, optimization | 4–5 days |
| **Phase 4** | Frontend UI | Upload, JD input, results panel, diff viewer | 4–5 days |
| **Phase 5** | PDF Export, Polish & Testing | PDF generation, end-to-end testing, final polish | 3–4 days |

---

## Phase 1 — Project Scaffolding & Setup

### Goals
- Initialize the project repository with both frontend and backend scaffolds
- Configure environment variables, dependencies, and dev tooling

### Tasks

#### 1.1 Repository Structure
```
resume-shapeshifter/
├── frontend/       ← React + Vite
├── backend/        ← FastAPI (Python)
├── docs/
├── .env.example
├── .gitignore
└── README.md
```

#### 1.2 Backend Setup
- [ ] Create Python virtual environment (`venv`)
- [ ] Install core dependencies:
  ```
  fastapi uvicorn python-multipart
  pdfplumber python-docx
  groq
  python-dotenv
  weasyprint
  ```
- [ ] Create `backend/main.py` — FastAPI app entry point with CORS config
- [ ] Create `.env.example`:
  ```
  GROQ_API_KEY=your_groq_api_key_here
  GROQ_MODEL_PRIMARY=llama-3.3-70b-versatile
  GROQ_MODEL_FALLBACK=mixtral-8x7b-32768
  ```
- [ ] Set up `backend/models/` — Pydantic models for `Resume`, `JobDescription`, `TailoredResume`

#### 1.3 Frontend Setup
- [ ] Initialize Vite + React app: `npm create vite@latest frontend -- --template react`
- [ ] Install dependencies: `react-router-dom`, `axios`
- [ ] Set up `src/index.css` — global design system (fonts, color tokens, layout utilities)
- [ ] Create base folder structure: `components/`, `pages/`, `assets/`

#### 1.4 Dev Environment
- [ ] Configure CORS in FastAPI to allow frontend dev server (`http://localhost:5173`)
- [ ] Add `requirements.txt` and `package.json` scripts

#### Deliverable
> A running "Hello World" on both `http://localhost:8000` (FastAPI) and `http://localhost:5173` (React)

---

## Phase 2 — Backend Core: Ingestion & Parsing

### Goals
- Build the Resume Ingestion Layer (PDF/DOCX → structured JSON)
- Build the JD Parser (raw text → structured JSON)
- Expose REST API endpoints for both

### Tasks

#### 2.1 Pydantic Data Models (`backend/models/`)

**`resume.py`**
```python
class ExperienceEntry(BaseModel):
    company: str
    role: str
    duration: str
    bullets: List[str]

class Resume(BaseModel):
    professional_summary: str
    experience: List[ExperienceEntry]
    skills: List[str]
    education: List[dict]
    projects: List[dict]
    certifications: List[str]
```

**`job_description.py`**
```python
class JobDescription(BaseModel):
    role_title: str
    required_skills: List[str]
    preferred_skills: List[str]
    responsibilities: List[str]
    experience_required: str
    keywords: List[str]
```

#### 2.2 Resume Parser (`backend/services/resume_parser.py`)
- [ ] **PDF parsing** using `pdfplumber` — extract raw text page by page
- [ ] **DOCX parsing** using `python-docx` — extract paragraphs and tables
- [ ] **Section detection** — regex/heuristic rules to split text into sections:
  - Professional Summary, Experience, Skills, Education, Projects
- [ ] **Bullet extraction** — parse experience bullets per role
- [ ] Return structured `Resume` Pydantic object

#### 2.3 JD Parser (`backend/services/jd_parser.py`)
- [ ] Accept raw JD text string
- [ ] Use regex + keyword matching to extract:
  - Skills (tech keywords, tools)
  - Responsibilities (sentence-level extraction)
  - Experience requirements (`X+ years`, etc.)
- [ ] Return structured `JobDescription` Pydantic object
- [ ] *(Optionally enhance with a lightweight Groq call for nuanced extraction)*

#### 2.4 API Endpoints (`backend/api/routes/`)

**`upload.py` — `POST /api/upload-resume`**
- [ ] Accept multipart file upload (PDF or DOCX)
- [ ] Validate file type and size (max 5MB)
- [ ] Call `resume_parser.py`, return structured `Resume` JSON

**`analyze.py` — `POST /api/analyze`**
- [ ] Accept `{ resume: Resume, job_description: JobDescription }`
- [ ] Pass to LLM Orchestration Layer (Phase 3)
- [ ] Return `{ match_score, missing_skills, experience_gaps, suggestions }`

**`optimize.py` — `POST /api/optimize`**
- [ ] Accept `{ resume: Resume, job_description: JobDescription, analysis: AnalysisReport }`
- [ ] Pass to Optimization Engine (Phase 3)
- [ ] Return `TailoredResume` object with full diff

#### Deliverable
> `POST /api/upload-resume` correctly parses a sample resume PDF/DOCX and returns structured JSON. JD parser correctly extracts skills and responsibilities from sample JD text.

---

## Phase 3 — LLM Integration: Groq Orchestration

### Goals
- Implement prompt engineering layer for all 4 LLM tasks
- Build the Resume Optimization Engine
- Wire LLM outputs to the API endpoints from Phase 2

### Tasks

#### 3.1 Groq Client Setup (`backend/services/llm_client.py`)
```python
from groq import Groq
import os

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def call_groq(prompt: str, model: str = None) -> dict:
    model = model or os.environ["GROQ_MODEL_PRIMARY"]
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content
```

#### 3.2 Prompt Templates (`backend/prompts/`)

| File | Task | Output Format |
|---|---|---|
| `match_analysis.txt` | Compare resume vs JD, compute score | `{ match_score, missing_skills, experience_gaps, suggestions }` |
| `bullet_rewrite.txt` | Rewrite experience bullets to align with JD | `{ rewrites: [{original, improved}] }` |
| `summary_optimize.txt` | Rewrite professional summary for role | `{ new_summary }` |
| `skill_rank.txt` | Reorder skills by JD relevance | `{ ranked_skills[] }` |

Each prompt file includes:
- Clear role instruction
- Input format specification
- Output JSON schema
- "Do not fabricate" constraint

#### 3.3 LLM Orchestration Layer (`backend/services/llm_orchestrator.py`)

**Prompt Chain (sequential):**

```
Step 1 → match_analysis(resume, jd)
              └─► analysis_report { match_score, missing_skills, gaps, suggestions }

Step 2 → bullet_rewrite(resume.experience, jd, analysis_report)
              └─► improved_bullets[]

Step 3 → summary_optimize(resume.summary, jd, analysis_report)
              └─► new_summary

Step 4 → skill_rank(resume.skills, jd.required_skills)
              └─► ranked_skills[]
```

- [ ] Implement each step as a separate function
- [ ] Add error handling + retry logic (Groq rate limits)
- [ ] Use fallback model (`mixtral-8x7b-32768`) for prompts exceeding token limits

#### 3.4 Resume Optimization Engine (`backend/services/optimizer.py`)
- [ ] Accept `resume`, `jd`, `llm_outputs` and assemble `TailoredResume`
- [ ] Track every change as a diff entry:
  ```python
  { "field": "experience[0].bullets[2]", "original": "...", "updated": "..." }
  ```
- [ ] Enforce integrity rules:
  - No new companies, roles, or dates introduced
  - Skills list only reordered, not expanded with fake skills
  - Original facts preserved verbatim where not rewritten

#### 3.5 Wire to API Endpoints
- [ ] Connect `POST /api/analyze` → `llm_orchestrator.analyze_match()`
- [ ] Connect `POST /api/optimize` → `optimizer.build_tailored_resume()`

#### Deliverable
> End-to-end backend test: submit a sample resume + JD via `curl` or Postman, receive a full `TailoredResume` JSON with match score, diff entries, and rewritten content.

---

## Phase 4 — Frontend UI

### Goals
- Build the complete user-facing interface
- Integrate with all backend API endpoints
- Implement a polished, responsive design

### Tasks

#### 4.1 Design System (`src/index.css`)
- [ ] Define CSS custom properties (color tokens, spacing, typography)
- [ ] Import Google Fonts (`Inter` or `Outfit`)
- [ ] Define dark-mode base theme
- [ ] Global utilities: card styles, button variants, input styles, badge styles

#### 4.2 Components

**`ResumeUploader.jsx`**
- [ ] Drag-and-drop zone with file preview
- [ ] Validate file type (PDF/DOCX) and size before upload
- [ ] On upload success → display extracted resume fields in a preview card
- [ ] Call `POST /api/upload-resume`

**`JDInputPanel.jsx`**
- [ ] Multi-line textarea for pasting job description
- [ ] Character counter
- [ ] "Clear" and "Paste from Clipboard" helper buttons
- [ ] Parse + display extracted JD fields (skills, role) on submission

**`AnalysisResultsPanel.jsx`**
- [ ] Animated match score gauge / donut chart (CSS or SVG)
- [ ] Missing Skills list with badge styling
- [ ] Experience Gaps list
- [ ] LLM suggestions in collapsible accordion

**`ResumeDiffViewer.jsx`**
- [ ] Side-by-side layout: Original (left) | Tailored (right)
- [ ] Highlighted diff — changed lines/bullets in amber, new content in green
- [ ] Toggle to view full resume vs changes only

**`DownloadButton.jsx`**
- [ ] Triggers `GET /api/download-pdf`
- [ ] Shows loading spinner during generation
- [ ] Downloads file as `tailored_resume_[role].pdf`

#### 4.3 Pages

**`Home.jsx`** — Main single-page layout:
```
[Header / Logo]
[Step 1: Resume Upload] → [Step 2: JD Input] → [Analyze Button]
[Results: Score Panel | Diff Viewer]
[Download Button]
```
- [ ] Multi-step progress indicator
- [ ] Loading states with skeleton placeholders during API calls
- [ ] Error toast notifications for failed requests

#### 4.4 API Integration (`src/api/`)
- [ ] `resumeApi.js` — upload resume, fetch analysis, fetch optimized resume, download PDF
- [ ] Axios instance with base URL config
- [ ] Global error handling interceptor

#### Deliverable
> Full UI running locally with all components connected to the backend. User can upload a resume, paste a JD, click "Tailor Resume," and see results displayed.

---

## Phase 5 — PDF Export, Polish & Testing

### Goals
- Implement downloadable side-by-side PDF export
- End-to-end testing and bug fixes
- Final UI/UX polish

### Tasks

#### 5.1 PDF Generation (`backend/services/pdf_generator.py`)
- [ ] Use `WeasyPrint` to render HTML → PDF
- [ ] Design PDF layout:
  - **Page 1:** Match Score Summary, Missing Skills, Experience Gaps
  - **Page 2+:** Side-by-side Original vs Tailored resume with change highlights
- [ ] Apply clean print-friendly CSS styling
- [ ] Expose via `GET /api/download-pdf` — stream PDF bytes as response

#### 5.2 API Endpoint (`backend/api/routes/download.py`)
- [ ] Accept `tailored_resume_id` or full `TailoredResume` payload
- [ ] Generate PDF via `pdf_generator.py`
- [ ] Return `StreamingResponse` with `Content-Disposition: attachment` header

#### 5.3 End-to-End Testing
- [ ] **Backend unit tests** (`pytest`):
  - `test_resume_parser.py` — test PDF and DOCX parsing with sample files
  - `test_jd_parser.py` — test JD extraction with sample JDs
  - `test_optimizer.py` — test diff tracking and integrity rules
- [ ] **API integration tests**:
  - Test all 4 endpoints with valid and invalid payloads
  - Test error handling (bad file type, empty JD, Groq API failure)
- [ ] **Frontend manual testing**:
  - Upload PDF resume → verify extracted fields
  - Paste JD → verify parsed skills
  - Click Analyze → verify score and diffs render correctly
  - Download PDF → verify layout

#### 5.4 Final Polish
- [ ] Responsive design — test on mobile and tablet viewports
- [ ] Accessibility — keyboard navigation, ARIA labels on interactive elements
- [ ] Loading & error states for all async actions
- [ ] SEO meta tags in `index.html` (title, description)
- [ ] `.env.example` documentation
- [ ] Update `README.md` with setup instructions and screenshots

#### Deliverable
> Fully functional application — user can upload a resume, input a JD, receive AI-tailored results, and download a formatted PDF. All core paths tested.

---

## Dependency Graph

```
Phase 1 (Scaffolding)
    │
    ├──► Phase 2 (Backend Parsing)
    │         │
    │         └──► Phase 3 (LLM + Optimization)
    │                   │
    └──► Phase 4 (Frontend UI)
              │
              └──► Phase 5 (PDF Export + Testing)  ◄── Phase 3
```

Phases 2 and 4 can run in parallel after Phase 1 is complete.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Groq rate limits during development | Medium | Medium | Use fallback model; cache LLM responses during testing |
| Poor section detection in resume parser | High | High | Build regex + heuristic rules; test against 5+ resume formats |
| LLM returns malformed JSON | Medium | High | Wrap all Groq calls with JSON validation + retry logic |
| WeasyPrint rendering issues on Windows | Low | Medium | Test early in Phase 5; fallback to Puppeteer (Node.js) |
| Large resume/JD exceeding token limits | Low | Medium | Use `mixtral-8x7b-32768` fallback (32k context window) |

---

## Environment Variables Reference

```env
# Groq LLM
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL_PRIMARY=llama-3.3-70b-versatile
GROQ_MODEL_FALLBACK=mixtral-8x7b-32768

# App Config
MAX_UPLOAD_SIZE_MB=5
ALLOWED_FILE_TYPES=pdf,docx
CORS_ORIGINS=http://localhost:5173
```
