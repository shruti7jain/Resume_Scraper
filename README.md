# Resume Shapeshifter ✦
### AI-Powered Resume Tailoring Engine

> Upload your resume. Paste a job description. Get an ATS-optimized, role-specific version — powered by **Groq + Llama 3.3**.

---

## What It Does

Resume Shapeshifter takes your **existing resume** and a **target job description (JD)** and uses AI to:

- Calculate a **Resume–JD Match Score**
- Identify **Missing Skills** and **Experience Gaps**
- Rewrite your bullets and summary to align with the JD
- Preserve all original facts — **no fabricated experience**
- Export a **side-by-side PDF comparison** (Original vs. Tailored)

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18 + Vite |
| **Styling** | Vanilla CSS |
| **Backend** | FastAPI (Python 3.11+) |
| **Resume Parsing** | `pdfplumber`, `python-docx` |
| **LLM Inference** | Groq API (`llama-3.3-70b-versatile`) |
| **PDF Export** | WeasyPrint |

---

## Project Structure

```
resume-shapeshifter/
├── frontend/                  # React + Vite SPA
│   ├── src/
│   │   ├── components/        # ResumeUploader, JDInputPanel, etc.
│   │   ├── pages/             # Home.jsx
│   │   ├── api/               # resumeApi.js (Axios calls)
│   │   ├── App.jsx
│   │   └── index.css          # Design system
│   └── index.html
│
├── backend/                   # FastAPI server
│   ├── api/routes/            # upload.py, analyze.py, optimize.py, download.py
│   ├── services/              # resume_parser, jd_parser, llm_orchestrator, optimizer, pdf_generator
│   ├── prompts/               # .txt prompt templates for Groq
│   ├── models/                # Pydantic schemas
│   └── main.py                # App entry point
│
├── docs/                      # Project documentation
│   ├── context.md
│   ├── architecture.md
│   ├── implementation_plan.md
│   ├── edge.md
│   ├── api.md
│   └── problemstatement.txt
│
├── .env.example
├── requirements.txt
└── README.md
```

---

## Prerequisites

- **Python** 3.11+
- **Node.js** 18+ and **npm**
- **Groq API Key** → Get one free at [console.groq.com](https://console.groq.com)
- **WeasyPrint system dependencies** (see [Platform Notes](#platform-notes))

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/resume-shapeshifter.git
cd resume-shapeshifter
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_PRIMARY=llama-3.3-70b-versatile
GROQ_MODEL_FALLBACK=mixtral-8x7b-32768
MAX_UPLOAD_SIZE_MB=5
ALLOWED_FILE_TYPES=pdf,docx
CORS_ORIGINS=http://localhost:5173
```

---

### 3. Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn backend.main:app --reload --port 8000
```

Backend will be running at: **http://localhost:8000**  
API docs (Swagger UI): **http://localhost:8000/docs**

---

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Frontend will be running at: **http://localhost:5173**

---

## Usage

1. **Open** `http://localhost:5173` in your browser
2. **Upload** your resume (PDF or DOCX, max 5MB)
3. **Paste** the job description into the JD panel
4. **Click** "Tailor My Resume"
5. **Review** your Match Score, Missing Skills, and rewritten resume
6. **Download** the side-by-side PDF comparison

---

## API Reference

See [`docs/api.md`](docs/api.md) for full endpoint documentation with request/response schemas and `curl` examples.

---

## Documentation Index

| Document | Description |
|---|---|
| [`docs/context.md`](docs/context.md) | Project context and objectives |
| [`docs/architecture.md`](docs/architecture.md) | System design and architecture |
| [`docs/implementation_plan.md`](docs/implementation_plan.md) | Phase-wise build plan |
| [`docs/edge.md`](docs/edge.md) | Edge cases and handling strategies |
| [`docs/api.md`](docs/api.md) | REST API reference |

---

## Platform Notes

### WeasyPrint System Dependencies

WeasyPrint requires native system libraries for PDF rendering.

**Windows:**
```bash
# Install GTK3 runtime from:
# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
```

**macOS:**
```bash
brew install pango libffi
```

**Ubuntu / Debian:**
```bash
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libgdk-pixbuf2.0-0
```

> If WeasyPrint cannot be installed, the PDF download feature will be disabled. All other features remain fully functional.

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | — | Your Groq API key |
| `GROQ_MODEL_PRIMARY` | No | `llama-3.3-70b-versatile` | Primary LLM model |
| `GROQ_MODEL_FALLBACK` | No | `mixtral-8x7b-32768` | Fallback for long-context inputs |
| `MAX_UPLOAD_SIZE_MB` | No | `5` | Max resume upload size in MB |
| `ALLOWED_FILE_TYPES` | No | `pdf,docx` | Accepted file extensions |
| `CORS_ORIGINS` | No | `http://localhost:5173` | Allowed frontend origin(s) |

---

## Key Design Principles

- **No fabrication** — The AI only rewrites and restructures your existing experience. It never invents new jobs, skills, or credentials.
- **Full transparency** — Every change is tracked and shown as a diff. You see exactly what was modified.
- **No data persistence** — Your resume is processed in-memory and never stored on disk or in a database.
- **Privacy-first** — Your resume content is only sent to Groq for LLM inference. No third-party analytics or storage.

---

## License

MIT License — see `LICENSE` for details.
