# Context: Resume Shapeshifter — AI-Powered Resume Tailoring Engine

## Problem Statement

You are tasked with building an **AI-powered resume tailoring application** that helps users improve an **existing resume** for a specific job description (JD). The system should intelligently analyze the resume and job requirements using a Large Language Model (LLM) and generate an **optimized version of the same resume** without creating fake experience.

---

## Objective

Design and implement an application that:

- Takes an existing resume and a target job description as input
- Uses AI to analyze how well the resume matches the role
- Leverages an LLM to suggest truthful improvements
- Shows comparison and insights in a clear format to the user

---

## System Workflow

### 1. Resume Ingestion

- Upload and preprocess the user's resume (PDF/DOCX)
- Extract relevant fields such as:
  - Professional Summary
  - Experience
  - Skills
  - Education
  - Projects

---

### 2. Job Description Input

- Collect job details:
  - Paste Job Description
  - Role Information
- Extract:
  - Required Skills
  - Keywords
  - Responsibilities
  - Experience Requirements

---

### 3. Integration + LLM Analysis Layer

- Combine Resume data and Job Description
- Pass structured information into LLM to:
  - Compare Resume with JD
  - Calculate Resume–JD Match Score
  - Identify Missing Skills
  - Detect Experience Gaps
  - Suggest improvement opportunities

---

### 4. Resume Optimization Engine

- Use LLM outputs to optimize the existing resume:
  - Rewrite resume bullets
  - Improve wording and clarity
  - Reorder skills based on relevance
  - Improve keyword alignment
  - Preserve original facts and experience

---

### 5. Output Display

- Present results in a user-friendly format:
  - Resume Match Score
  - Original Resume
  - Tailored Resume (Optimized Version)
  - Missing Skills
  - Experience Gaps
  - Highlighted Changes
  - Downloadable Side-by-Side PDF

---

## Expected Outcome

Users should be able to transform a generic resume into a **role-specific and ATS-friendly version** in minutes while keeping their experience accurate and transparent, reducing manual editing effort and improving application readiness.
