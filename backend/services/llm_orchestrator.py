"""
LLM Orchestration Layer — Phase 3 Implementation

Coordinates the 4-step Groq prompt chain:
  Step 1 → match_analysis  → AnalysisReport
  Step 2 → bullet_rewrite  → improved bullets per experience entry
  Step 3 → summary_optimize → new professional summary
  Step 4 → skill_rank      → JD-ordered skills list

Each step is a standalone async function so the optimizer can call them
individually or the full chain can be run in sequence.
"""

import json
import logging
from copy import deepcopy
from typing import Any

from backend.models.resume import Resume
from backend.models.job_description import JobDescription
from backend.models.tailored_resume import AnalysisReport
from backend.services import llm_client

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Step 1 — Match Analysis
# ---------------------------------------------------------------------------

async def analyze_match(resume: Resume, jd: JobDescription) -> AnalysisReport:
    """
    Step 1 of the LLM pipeline: compare resume vs JD, return an AnalysisReport.

    Calls match_analysis.txt prompt with resume + JD JSON.
    Returns a validated AnalysisReport with match_score, missing_skills,
    experience_gaps, and suggestions.
    """
    template = llm_client.load_prompt("match_analysis.txt")

    resume_json = json.dumps(resume.model_dump(exclude_none=True), indent=2)
    jd_json     = json.dumps(jd.model_dump(exclude_none=True, exclude={"raw_text"}), indent=2)

    prompt = template.replace("{{resume_json}}", resume_json).replace("{{jd_json}}", jd_json)

    logger.info("Step 1 — Running match analysis (resume: %s, role: %s)", resume.name, jd.role_title)
    raw = llm_client.call_groq(prompt)

    return AnalysisReport(
        match_score=_clamp(int(raw.get("match_score", 0)), 0, 100),
        missing_skills=_ensure_list(raw.get("missing_skills", [])),
        experience_gaps=_ensure_list(raw.get("experience_gaps", [])),
        suggestions=_ensure_list(raw.get("suggestions", [])),
    )


# ---------------------------------------------------------------------------
# Step 2 — Bullet Rewriting
# ---------------------------------------------------------------------------

async def rewrite_bullets(
    resume: Resume,
    jd: JobDescription,
    analysis: AnalysisReport,
) -> list[dict[str, Any]]:
    """
    Step 2 of the LLM pipeline: rewrite experience bullets for JD alignment.

    Collects all bullets across all experience entries, sends them in one
    prompt call, and returns a list of {original, improved} pairs.

    Returns:
        List of dicts: [{"original": str, "improved": str}, ...]
    """
    # Flatten all bullets with their location metadata
    all_bullets: list[dict[str, Any]] = []
    for exp_idx, exp in enumerate(resume.experience):
        for b_idx, bullet in enumerate(exp.bullets):
            all_bullets.append({
                "exp_index": exp_idx,
                "bullet_index": b_idx,
                "company": exp.company,
                "role": exp.role,
                "text": bullet,
            })

    if not all_bullets:
        logger.info("Step 2 — No bullets to rewrite, skipping.")
        return []

    template = llm_client.load_prompt("bullet_rewrite.txt")

    jd_summary = (
        f"Role: {jd.role_title}\n"
        f"Required Skills: {', '.join(jd.required_skills[:15])}\n"
        f"Keywords: {', '.join(jd.keywords[:20])}"
    )

    analysis_context = (
        f"Missing Skills: {', '.join(analysis.missing_skills[:10])}\n"
        f"Suggestions: {'; '.join(analysis.suggestions[:5])}"
    )

    bullets_json = json.dumps(
        [{"original": b["text"], "company": b["company"], "role": b["role"]} for b in all_bullets],
        indent=2,
    )

    prompt = (
        template
        .replace("{{jd_summary}}", jd_summary)
        .replace("{{analysis_context}}", analysis_context)
        .replace("{{bullets_json}}", bullets_json)
    )

    logger.info("Step 2 — Rewriting %d bullets for %d experience entries",
                len(all_bullets), len(resume.experience))
    raw = llm_client.call_groq(prompt)

    rewrites: list[dict] = raw.get("rewrites", [])

    # Map back: merge location metadata with rewrite result
    result = []
    for i, entry in enumerate(all_bullets):
        if i < len(rewrites):
            result.append({
                "exp_index":    entry["exp_index"],
                "bullet_index": entry["bullet_index"],
                "original":     entry["text"],
                "improved":     rewrites[i].get("improved", entry["text"]),
            })
        else:
            # LLM returned fewer rewrites than bullets — keep original
            result.append({
                "exp_index":    entry["exp_index"],
                "bullet_index": entry["bullet_index"],
                "original":     entry["text"],
                "improved":     entry["text"],
            })

    return result


# ---------------------------------------------------------------------------
# Step 3 — Summary Optimization
# ---------------------------------------------------------------------------

async def optimize_summary(
    resume: Resume,
    jd: JobDescription,
    analysis: AnalysisReport,
) -> str:
    """
    Step 3: Rewrite the professional summary to target the specific JD role.

    Returns the new summary string.
    """
    template = llm_client.load_prompt("summary_optimize.txt")

    # Build a compact resume context (name + first 2 experience entries)
    resume_context_parts = []
    if resume.name:
        resume_context_parts.append(f"Name: {resume.name}")
    for exp in resume.experience[:2]:
        resume_context_parts.append(f"- {exp.role} at {exp.company} ({exp.duration})")
    resume_context = "\n".join(resume_context_parts)

    jd_keywords = ", ".join(
        (jd.required_skills + jd.keywords)[:20]
    )

    prompt = (
        template
        .replace("{{role_title}}", jd.role_title)
        .replace("{{jd_keywords}}", jd_keywords)
        .replace("{{original_summary}}", resume.professional_summary or "(no summary provided)")
        .replace("{{resume_context}}", resume_context)
        .replace("{{suggestions}}", "; ".join(analysis.suggestions[:4]))
    )

    logger.info("Step 3 — Optimizing professional summary for role: %s", jd.role_title)
    raw = llm_client.call_groq(prompt)

    new_summary = raw.get("new_summary", "")
    if not new_summary or len(new_summary) < 20:
        logger.warning("Step 3 — LLM returned empty/short summary; keeping original.")
        return resume.professional_summary

    return new_summary.strip()


# ---------------------------------------------------------------------------
# Step 4 — Skill Ranking
# ---------------------------------------------------------------------------

async def rank_skills(
    resume: Resume,
    jd: JobDescription,
) -> list[str]:
    """
    Step 4: Reorder skills by JD relevance — no additions or removals.

    Returns a reordered copy of resume.skills.
    """
    if not resume.skills:
        return []

    template = llm_client.load_prompt("skill_rank.txt")

    prompt = (
        template
        .replace("{{required_skills}}", json.dumps(jd.required_skills))
        .replace("{{preferred_skills}}", json.dumps(jd.preferred_skills))
        .replace("{{candidate_skills}}", json.dumps(resume.skills))
    )

    logger.info("Step 4 — Ranking %d skills against JD", len(resume.skills))
    raw = llm_client.call_groq(prompt)

    ranked = raw.get("ranked_skills", [])

    # Integrity check: returned list must be same set as input
    original_set = {s.lower() for s in resume.skills}
    returned_set = {s.lower() for s in ranked}

    if returned_set != original_set:
        logger.warning(
            "Step 4 — Skill integrity violation: LLM added/removed skills. "
            "Falling back to JD-ordered heuristic."
        )
        return _heuristic_skill_rank(resume.skills, jd)

    return ranked


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

async def run_full_pipeline(
    resume: Resume,
    jd: JobDescription,
) -> dict[str, Any]:
    """
    Run all 4 steps sequentially and return a dict with all outputs.

    Returns:
        {
            "analysis":       AnalysisReport,
            "bullet_rewrites": list[dict],
            "new_summary":    str,
            "ranked_skills":  list[str],
        }
    """
    logger.info("=== LLM Pipeline START — %s → %s ===", resume.name, jd.role_title)

    # Step 1
    analysis = await analyze_match(resume, jd)
    logger.info("Step 1 done — match_score=%d", analysis.match_score)

    # Step 2
    bullet_rewrites = await rewrite_bullets(resume, jd, analysis)
    logger.info("Step 2 done — %d bullets rewritten", len(bullet_rewrites))

    # Step 3
    new_summary = await optimize_summary(resume, jd, analysis)
    logger.info("Step 3 done — summary length=%d chars", len(new_summary))

    # Step 4
    ranked_skills = await rank_skills(resume, jd)
    logger.info("Step 4 done — %d skills ranked", len(ranked_skills))

    logger.info("=== LLM Pipeline END ===")

    return {
        "analysis":        analysis,
        "bullet_rewrites": bullet_rewrites,
        "new_summary":     new_summary,
        "ranked_skills":   ranked_skills,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def _ensure_list(val: Any) -> list:
    if isinstance(val, list):
        return [str(item) for item in val]
    if isinstance(val, str):
        return [val] if val else []
    return []


def _heuristic_skill_rank(skills: list[str], jd: JobDescription) -> list[str]:
    """
    Fallback: sort skills by JD relevance without LLM.
    Priority: required > preferred > rest (original order preserved within each group).
    """
    req_lower  = {s.lower() for s in jd.required_skills}
    pref_lower = {s.lower() for s in jd.preferred_skills}

    required  = [s for s in skills if s.lower() in req_lower]
    preferred = [s for s in skills if s.lower() in pref_lower and s.lower() not in req_lower]
    rest      = [s for s in skills if s.lower() not in req_lower and s.lower() not in pref_lower]

    return required + preferred + rest
