# Edge Cases: Resume Shapeshifter
## Corner Scenarios & Handling Guide

> This document catalogs all known edge cases, boundary conditions, and failure scenarios across every layer of the Resume Shapeshifter system, along with recommended handling strategies.

---

## Table of Contents

1. [File Upload & Ingestion](#1-file-upload--ingestion)
2. [Resume Parsing](#2-resume-parsing)
3. [Job Description Input & Parsing](#3-job-description-input--parsing)
4. [LLM Orchestration (Groq)](#4-llm-orchestration-groq)
5. [Resume Optimization Engine](#5-resume-optimization-engine)
6. [Match Score & Analysis](#6-match-score--analysis)
7. [PDF Generation](#7-pdf-generation)
8. [Frontend UI](#8-frontend-ui)
9. [Security & Abuse](#9-security--abuse)
10. [Environment & Configuration](#10-environment--configuration)

---

## 1. File Upload & Ingestion

| # | Edge Case | Scenario | Expected Handling |
|---|---|---|---|
| 1.1 | **Unsupported file type** | User uploads `.jpg`, `.txt`, `.xlsx`, `.pptx` | Return `400 Bad Request` with message: "Only PDF and DOCX files are supported." |
| 1.2 | **File too large** | Resume exceeds 5MB limit | Reject before processing; return `413 Payload Too Large` with size limit info |
| 1.3 | **Empty file** | User uploads a 0-byte or blank PDF/DOCX | Detect empty content after parsing; return `422` with "Uploaded file appears to be empty." |
| 1.4 | **Password-protected PDF** | Encrypted PDF that requires a password to open | `pdfplumber` raises an exception; catch and return `422`: "PDF is password-protected. Please upload an unlocked version." |
| 1.5 | **Scanned / image-only PDF** | PDF contains only scanned images (no selectable text) | Text extraction returns empty string; notify user: "Resume appears to be a scanned image. Please upload a text-based PDF." *(OCR support is a future enhancement)* |
| 1.6 | **Corrupted file** | File bytes are malformed / truncated | Parser raises `Exception`; return `422`: "File could not be read. It may be corrupted." |
| 1.7 | **Duplicate upload** | User uploads the same file twice in the same session | Silently overwrite the previous upload and re-parse |
| 1.8 | **Multi-file upload attempt** | User drops multiple files at once | Accept only the first file; display a warning: "Only one resume can be processed at a time." |
| 1.9 | **Very slow upload** | User is on a slow connection and upload stalls | Implement a 30-second request timeout; surface a retry message on timeout |
| 1.10 | **DOCX with embedded images / charts** | Resume has logos, headshot, or graph objects | Skip non-text elements silently; extract only text content |

---

## 2. Resume Parsing

| # | Edge Case | Scenario | Expected Handling |
|---|---|---|---|
| 2.1 | **Non-standard section headings** | Resume uses "Work History" instead of "Experience", "Competencies" instead of "Skills" | Implement fuzzy/alias matching for section headers; maintain a synonym dictionary |
| 2.2 | **No section headings at all** | Plain prose resume with no labeled sections | Fall back to full-text extraction; flag to LLM that structure is unformatted |
| 2.3 | **Missing key sections** | Resume has no Skills section or no Professional Summary | Set missing fields to `null` / empty array; do not fail the parse; inform LLM of absence |
| 2.4 | **Multiple roles at same company** | Candidate held 2–3 positions at one employer | Correctly parse as separate `ExperienceEntry` objects under the same company |
| 2.5 | **Date format variations** | `Jan 2021 – Present`, `01/2021–current`, `2021–now` | Normalize all date strings to `MM/YYYY` format; treat "Present/Current/Now" as present |
| 2.6 | **Non-English resume** | Resume is written in French, Spanish, German, etc. | Attempt parse; flag language in metadata; display warning: "Non-English resumes may produce lower quality results." |
| 2.7 | **Extremely long resume** | 10+ page academic CV with 50+ publications | Truncate to a configurable max token count before sending to Groq; warn user |
| 2.8 | **Single-page resume with minimal content** | Only name, email, and 2 bullet points | Parse successfully; LLM will produce lower match score and more suggestions |
| 2.9 | **Multi-column layout PDF** | Two-column resume where text extraction scrambles order | Text may be read column-by-column out of order; add column-merge heuristics or warn user |
| 2.10 | **Skills listed inline in experience** | Skills embedded in bullets, not in a dedicated Skills section | LLM analysis should still detect these skills contextually; no failure |
| 2.11 | **Unicode / special characters** | Bullets using `•`, `→`, `▪`, or accented characters in names | Normalize Unicode; strip or replace decorative symbols in bullet extraction |
| 2.12 | **Hyperlinks in resume** | Email, LinkedIn, GitHub URLs embedded in text | Strip or preserve as metadata; do not let URLs pollute the text content of bullets |
| 2.13 | **Tables in DOCX** | Skills presented as a table in Word format | Use `python-docx` table iterator to extract cell text; merge into skills list |

---

## 3. Job Description Input & Parsing

| # | Edge Case | Scenario | Expected Handling |
|---|---|---|---|
| 3.1 | **Empty JD** | User submits with blank JD field | Block submission; show inline validation: "Please paste a job description before continuing." |
| 3.2 | **JD is too short** | User pastes only the job title (e.g., "Software Engineer at Google") | Warn: "Job description seems too brief. Please include responsibilities and requirements." Still allow submission. |
| 3.3 | **JD is extremely long** | 5,000+ word JD with extensive company boilerplate | Truncate to top 3,000 tokens before sending to Groq; summarize boilerplate sections |
| 3.4 | **JD in different language** | Non-English job description | Flag mismatch if resume is in English; warn user that cross-language tailoring may be inaccurate |
| 3.5 | **JD without listed skills** | Narrative-style JD with no explicit skill keywords | LLM must infer implicit skills from responsibilities; match score may be less precise |
| 3.6 | **JD with contradictory requirements** | "3+ years experience required" for an entry-level role | Pass as-is to LLM; it will reflect the contradiction in its analysis |
| 3.7 | **JD for a field completely unrelated to resume** | Software engineer resume vs. Chef job posting | LLM returns very low match score; clearly communicate the mismatch to the user |
| 3.8 | **Copy-paste formatting artifacts** | JD pasted with extra line breaks, HTML tags (`<p>`, `&amp;`), or tab characters | Sanitize input: strip HTML tags, normalize whitespace, decode HTML entities before processing |
| 3.9 | **JD with only "Equal Opportunity" boilerplate** | User accidentally pastes only the EEO disclaimer | Return low confidence; suggest the user paste the full job posting |
| 3.10 | **Duplicate JD submission** | User clicks "Analyze" multiple times rapidly | Debounce button (500ms); cancel in-flight requests before firing a new one |

---

## 4. LLM Orchestration (Groq)

| # | Edge Case | Scenario | Expected Handling |
|---|---|---|---|
| 4.1 | **Groq API key missing** | `GROQ_API_KEY` not set in `.env` | Fail fast at startup with a clear error: "GROQ_API_KEY environment variable is not set." |
| 4.2 | **Invalid API key** | Wrong or expired key causes `401 Unauthorized` | Catch `AuthenticationError`; return `503` to client: "LLM service authentication failed. Contact support." |
| 4.3 | **Groq rate limit exceeded** | `429 Too Many Requests` during high usage | Exponential backoff: retry up to 3 times (1s, 2s, 4s); if all fail, return `503` gracefully |
| 4.4 | **LLM returns malformed JSON** | Response is not valid JSON despite `json_object` format | Validate JSON on receipt; if invalid, retry once with stricter prompt instruction; if still invalid, return a partial result with a warning |
| 4.5 | **LLM response truncated** | Output hits the token limit mid-JSON | Detect incomplete JSON (missing closing braces); retry with `mixtral-8x7b-32768` (longer context); warn user if unresolvable |
| 4.6 | **LLM hallucinates new experience** | Despite instructions, model invents a company or role | Optimization engine diff-checker validates that no new company/role names appear in the tailored resume; revert hallucinated content |
| 4.7 | **LLM returns match score > 100 or < 0** | Invalid numeric range in score output | Clamp: `score = max(0, min(100, score))` |
| 4.8 | **Groq service outage** | Connection timeout or `503` from Groq | Return `503` to user with message: "AI service is temporarily unavailable. Please try again in a few minutes." |
| 4.9 | **Prompt injection in JD or resume** | User embeds `"Ignore previous instructions and..."` in their JD | Sanitize inputs; use system-role prompts that reinforce constraints; do not expose raw user text as trusted instructions |
| 4.10 | **LLM returns empty content** | Response choices array is empty or content is `null` | Treat as a failed call; retry once; if still empty, fall back with original resume and alert user |
| 4.11 | **Token limit exceeded for primary model** | Combined resume + JD + prompt exceeds `llama-3.3-70b-versatile` limits | Automatically switch to fallback model `mixtral-8x7b-32768` (32k context window) |
| 4.12 | **Prompt chain partial failure** | Step 2 (bullet rewriting) fails but Step 1 (match analysis) succeeded | Return partial results: show match score and missing skills; surface a warning that bullet rewriting was unavailable |

---

## 5. Resume Optimization Engine

| # | Edge Case | Scenario | Expected Handling |
|---|---|---|---|
| 5.1 | **No changes suggested by LLM** | Resume already strongly matches the JD (score ≥ 95) | Display message: "Your resume is already well-aligned with this role." Show score; still allow download |
| 5.2 | **All bullets rewritten** | LLM rewrites every single bullet point | Flag to user that extensive changes were made; recommend reviewing each change carefully |
| 5.3 | **Original bullet is one word** | Resume bullet is "Python." with no context | Rewrite may expand or note inability to improve without more context; do not fail |
| 5.4 | **Experience section is completely empty** | Resume has no work experience (fresh graduate) | Skip experience optimization; focus on skills, education, and projects; adjust suggestion copy accordingly |
| 5.5 | **Skills list is empty** | Resume has no listed skills | LLM may extract implicit skills from bullets; if none found, suggest user add a skills section |
| 5.6 | **Identical original and rewritten bullet** | LLM returns the same text for original and improved | Exclude from diff — do not show a "change" where nothing changed |
| 5.7 | **Rewritten text is longer than original** | Optimization expands bullets significantly | Accept; no length constraint imposed. User may review and trim. |
| 5.8 | **Candidate has more experience than JD requires** | 10-year engineer applying for a junior role | Do not downplay experience; note the seniority gap in analysis; suggest appropriate framing |
| 5.9 | **Missing skills are completely different domain** | JD requires Kubernetes; resume has no DevOps at all | List in "Missing Skills" honestly; do not fabricate proficiency; suggest the user acknowledge the gap in a cover letter |
| 5.10 | **Projects section heavily matches JD** | Personal project uses same tech as JD | Promote project relevance in the tailored resume; surface this as a strength in the match analysis |

---

## 6. Match Score & Analysis

| # | Edge Case | Scenario | Expected Handling |
|---|---|---|---|
| 6.1 | **Score of 0%** | Completely mismatched resume and JD | Display clearly with explanation; do not block user from viewing analysis or downloading |
| 6.2 | **Score of 100%** | Perfect match | Display with a "Great match!" badge; verify this is not a hallucination (check that LLM found no gaps) |
| 6.3 | **Missing skills list is empty** | LLM finds no missing skills despite low score | Surface other reasons for low score (wording, keyword density, experience gaps) |
| 6.4 | **Hundreds of missing skills returned** | Overly verbose LLM response lists trivial or implied skills | Cap display to top 10–15 most impactful missing skills; group minor ones under "Other" |
| 6.5 | **Experience gap analysis is inaccurate** | LLM misreads a date range and flags a gap that doesn't exist | Treat as a suggestion, not a fact; always prefix gap descriptions with "Possible gap detected:" |
| 6.6 | **Inconsistent scores across retries** | Re-running the same inputs returns different scores | This is expected LLM non-determinism; display a disclaimer: "Match scores may vary slightly." |

---

## 7. PDF Generation

| # | Edge Case | Scenario | Expected Handling |
|---|---|---|---|
| 7.1 | **WeasyPrint not installed** | Dependency missing in production environment | Catch `ImportError` at startup; log a clear error; disable PDF download button with tooltip: "PDF export is currently unavailable." |
| 7.2 | **Very long tailored resume** | Resume content causes 10+ page PDF | Do not truncate; allow multi-page output; ensure page breaks are clean |
| 7.3 | **Special characters in resume break HTML template** | `<`, `>`, `&`, `"` in resume content | HTML-escape all user content before injecting into the PDF template |
| 7.4 | **PDF generation times out** | Large resume causes WeasyPrint to take >30s | Set a 30-second timeout; if exceeded, return `504` with message: "PDF generation timed out. Please try again." |
| 7.5 | **No changes in diff** | Resume unchanged; side-by-side PDF looks identical | Still generate PDF; add a header note: "No significant changes were made to this resume." |
| 7.6 | **User downloads PDF before analysis completes** | Download triggered before `TailoredResume` is ready | Disable download button until analysis and optimization are complete; show disabled state with tooltip |
| 7.7 | **Non-ASCII characters in PDF** | Arabic, Chinese, or special symbols in resume | Ensure PDF template uses a Unicode-compatible font (e.g., `Noto Sans`); test explicitly |

---

## 8. Frontend UI

| # | Edge Case | Scenario | Expected Handling |
|---|---|---|---|
| 8.1 | **User navigates away mid-process** | Closes tab or clicks back during analysis | Warn with a browser dialog: "Analysis in progress. Are you sure you want to leave?" (use `beforeunload` event) |
| 8.2 | **Network drops during API call** | Internet disconnects while waiting for Groq response | Surface network error toast: "Connection lost. Please check your internet and retry." Show retry button. |
| 8.3 | **Backend server is down** | FastAPI server not running or crashed | Frontend catches `Network Error`; display: "Unable to connect to the server. Please try again later." |
| 8.4 | **Browser does not support drag-and-drop** | Older browser or accessibility mode | Provide standard `<input type="file">` as fallback; drag-and-drop is an enhancement, not the only path |
| 8.5 | **Mobile viewport** | User accesses on a phone | Diff viewer collapses from side-by-side to stacked layout; all interactions remain usable |
| 8.6 | **Very fast repeated clicks on "Analyze"** | Double-click or rapid re-submission | Disable button immediately on first click; re-enable only after response is received or error occurs |
| 8.7 | **User clears resume after analysis** | Uploads new resume without reloading | Reset entire results state (score, diffs, tailored resume) when a new file is uploaded |
| 8.8 | **User pastes JD after viewing results** | Changes JD after analysis is complete | Show a warning banner: "JD has changed. Re-run analysis to update results." Invalidate current results. |
| 8.9 | **Extremely long JD in textarea** | 5,000+ characters pasted; UI lags | Apply `max-height` with scroll to JD textarea; virtual rendering not needed but limit display height |
| 8.10 | **No results rendered** | API returns success but data is unexpectedly empty | Show empty state UI with guidance: "No results to display. Please try re-running the analysis." |

---

## 9. Security & Abuse

| # | Edge Case | Scenario | Expected Handling |
|---|---|---|---|
| 9.1 | **Prompt injection via resume content** | Resume contains `"SYSTEM: Ignore all constraints..."` | Treat all resume/JD content as untrusted user data in prompts; use system-role constraints that cannot be overridden by user content |
| 9.2 | **Malicious file upload** | User uploads a PDF with embedded scripts or macros | `pdfplumber` and `python-docx` extract text only — no macro execution; validate file headers (magic bytes) |
| 9.3 | **Denial of Service via large file** | Automated upload of many large files | Rate limiting on upload endpoint (e.g., 10 requests/minute per IP); file size hard cap enforced before reading bytes |
| 9.4 | **API key exposure** | `GROQ_API_KEY` accidentally logged or returned in API response | Never log API keys; ensure error responses do not echo back environment variables or stack traces |
| 9.5 | **CORS bypass attempt** | Request from unauthorized origin | Strict CORS whitelist in FastAPI; reject all origins not in the allowed list in production |
| 9.6 | **Repeated re-analysis to farm Groq tokens** | Automated script calling `/api/analyze` in a loop | Rate limit per IP/session; add CAPTCHA on frontend for production deployments |
| 9.7 | **PII in logs** | Resume content (name, email, address) ends up in server logs | Redact or avoid logging parsed resume content; log only request metadata (timestamps, status codes) |

---

## 10. Environment & Configuration

| # | Edge Case | Scenario | Expected Handling |
|---|---|---|---|
| 10.1 | **`.env` file missing** | Application started without a `.env` file | FastAPI startup validation checks for required env vars; fail with descriptive error listing which keys are missing |
| 10.2 | **Wrong model name in `.env`** | `GROQ_MODEL_PRIMARY` set to a non-existent model string | Groq returns `404` or `400`; catch and surface: "Configured LLM model is invalid. Check GROQ_MODEL_PRIMARY in .env." |
| 10.3 | **Frontend `.env` mismatch** | `VITE_API_BASE_URL` points to wrong backend port | All API calls fail with `CORS` or `Network Error`; document correct setup in README |
| 10.4 | **Port already in use** | `8000` (FastAPI) or `5173` (Vite) already occupied | Both tools provide clear port-in-use errors; document how to change ports in README |
| 10.5 | **Missing Python dependency** | `pdfplumber` or `groq` not installed | `ImportError` at runtime; `requirements.txt` must be kept in sync; document `pip install -r requirements.txt` as first setup step |
| 10.6 | **WeasyPrint system dependency missing** | WeasyPrint requires system libs (`libpango`, etc.) not installed | Document OS-level dependencies in README for Windows, macOS, and Linux; catch the import error gracefully |

---

## Summary Severity Matrix

| Severity | Count | Examples |
|---|---|---|
| 🔴 **Critical** (must handle before launch) | 12 | Password-protected PDF, Groq outage, prompt injection, missing API key, empty file |
| 🟡 **High** (handle in Phase 2–3) | 18 | Scanned PDF, malformed JSON from LLM, rate limits, non-standard section headers, token overflow |
| 🟢 **Medium** (handle in Phase 4–5) | 20 | Mobile layout, double-click protection, duplicate upload, stale results warning |
| ⚪ **Low** (future enhancement) | 10+ | Non-English resume support, OCR for scanned PDFs, multi-JD comparison |
