# Deployment Plan: Resume Shapeshifter

This document outlines the end-to-end deployment strategy for the Resume Shapeshifter application. The architecture consists of a Python FastAPI backend and a React (Vite) frontend.

---

## 1. Architecture Overview

- **Backend:** FastAPI (Python), serving REST APIs and generating PDFs via `xhtml2pdf`.
- **Frontend:** React + Vite, deployed as a static Single Page Application (SPA).
- **LLM Provider:** Groq (Llama 3 / Mixtral models).

Because the backend and frontend are decoupled, it is highly recommended to deploy them as **two separate services**.

---

## 2. Backend Deployment (FastAPI)

**Recommended Platforms:** Railway, Render, or Heroku.

### Prerequisites
1. **Procfile:** Ensure a `Procfile` exists at the root of the repository so PaaS builders know how to start the app.
   ```text
   web: uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
   ```
2. **Requirements:** `requirements.txt` must be up to date and include `fastapi`, `uvicorn`, `xhtml2pdf`, `groq`, `python-multipart`, etc.

### Steps (e.g., using Railway)
1. Connect your GitHub repository to Railway.
2. Create a new service from the repository. Railway will automatically detect Python and install dependencies via `pip`.
3. Go to the **Variables** tab for the backend service and add your secrets:
   - `GROQ_API_KEY`: Your private API key from Groq.
   - `GROQ_MODEL_PRIMARY`: `llama-3.3-70b-versatile` (optional, defaults in code).
   - `GROQ_MODEL_FALLBACK`: `mixtral-8x7b-32768` (optional).
4. Once deployed, Railway will provide a public URL (e.g., `https://resume-backend.up.railway.app`). **Save this URL.**

---

## 3. Frontend Deployment (React + Vite)

**Recommended Platforms:** Vercel, Netlify, or Railway. (Vercel is highly recommended for Vite apps).

### Prerequisites
You must update the API base URL in the frontend so it points to the live backend instead of `localhost`.
1. Open your frontend API configuration (or wherever `axios` is initialized).
2. Replace `http://localhost:8000` with your new live backend URL (e.g., `https://resume-backend.up.railway.app`). 
*(Note: A best practice is to use an environment variable like `import.meta.env.VITE_API_URL` instead of hardcoding it).*

### Steps (e.g., using Vercel)
1. Log into Vercel and click **Add New Project**.
2. Import your GitHub repository.
3. In the "Build and Output Settings":
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Click **Deploy**. Vercel will build the React app and give you a public URL (e.g., `https://resume-shapeshifter.vercel.app`).

---

## 4. CORS Configuration (Crucial Step)

For security reasons, web browsers block frontend apps from talking to backends on different domains unless explicitly allowed.

Once your frontend is deployed and has a public URL, you **must** update your FastAPI backend to allow traffic from that URL.

1. Open `backend/main.py`.
2. Find the CORS middleware configuration:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173", "https://resume-shapeshifter.vercel.app"], # <-- Add your live frontend URL here
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
3. Commit and push this change to GitHub. Railway will automatically rebuild the backend with the updated security rules.

---

## 5. Post-Deployment Checklist

- [ ] **Upload Test:** Can you successfully upload a PDF/DOCX on the live site?
- [ ] **LLM Test:** Does clicking "Analyze & Tailor" successfully communicate with Groq without timing out?
- [ ] **PDF Test:** Does the "Download Tailored PDF" button successfully stream the file to the browser?
- [ ] **Mobile Layout:** Check the live URL on a phone to ensure CSS responsiveness holds up.
