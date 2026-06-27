"""
Resume Optimization Engine — Phase 3 Implementation

Assembles the final TailoredResume from LLM pipeline outputs.
Enforces strict integrity rules:
  - No new companies, roles, or dates introduced
  - Skills list only reordered — never expanded
  - Every change is tracked as a DiffEntry for the diff viewer
"""

import uuid
import logging
from copy import deepcopy
from typing import Any

from backend.models.resume import Resume, ExperienceEntry
from backend.models.job_description import JobDescription
from backend.models.tailored_resume import TailoredResume, AnalysisReport, DiffEntry

logger = logging.getLogger(__name__)


async def build_tailored_resume(
    resume: Resume,
    jd: JobDescription,
    analysis: AnalysisReport,
    bullet_rewrites: list[dict[str, Any]],
    new_summary: str,
    ranked_skills: list[str],
) -> TailoredResume:
    """
    Assemble the optimized resume from LLM pipeline outputs.

    Applies changes in this order:
      1. Professional summary update
      2. Experience bullet rewrites
      3. Skill reordering

    Tracks every change as a DiffEntry.
    Enforces integrity: no new companies, roles, dates, or fabricated skills.

    Args:
        resume:          Original parsed resume
        jd:              Structured job description
        analysis:        AnalysisReport from Step 1
        bullet_rewrites: List of {exp_index, bullet_index, original, improved} dicts
        new_summary:     Rewritten summary string from Step 3
        ranked_skills:   Reordered skills list from Step 4

    Returns:
        TailoredResume with full diff tracking
    """
    logger.info("Optimizer — building tailored resume for %s → %s", resume.name, jd.role_title)

    # Deep-copy the original so we never mutate it
    tailored = deepcopy(resume)
    changes:  list[DiffEntry] = []

    # ------------------------------------------------------------------ #
    # 1. Professional summary
    # ------------------------------------------------------------------ #
    original_summary = resume.professional_summary or ""
    if new_summary and new_summary != original_summary:
        tailored.professional_summary = new_summary
        changes.append(DiffEntry(
            field="professional_summary",
            original=original_summary,
            updated=new_summary,
        ))
        logger.debug("Summary updated (%d → %d chars)", len(original_summary), len(new_summary))

    # ------------------------------------------------------------------ #
    # 2. Experience bullets
    # ------------------------------------------------------------------ #
    # Build a lookup: (exp_index, bullet_index) → improved text
    bullet_map: dict[tuple[int, int], str] = {}
    for entry in bullet_rewrites:
        key = (entry["exp_index"], entry["bullet_index"])
        bullet_map[key] = entry["improved"]

    original_companies = {exp.company.lower() for exp in resume.experience}
    original_roles     = {exp.role.lower() for exp in resume.experience}

    for exp_idx, exp in enumerate(tailored.experience):
        # --- Integrity: ensure company/role/duration unchanged ---
        original_exp = resume.experience[exp_idx]
        if exp.company != original_exp.company:
            logger.error("INTEGRITY VIOLATION: company changed. Reverting.")
            exp.company = original_exp.company
        if exp.role != original_exp.role:
            logger.error("INTEGRITY VIOLATION: role changed. Reverting.")
            exp.role = original_exp.role
        if exp.duration != original_exp.duration:
            logger.error("INTEGRITY VIOLATION: duration changed. Reverting.")
            exp.duration = original_exp.duration

        # Apply bullet rewrites
        for b_idx, original_bullet in enumerate(original_exp.bullets):
            key = (exp_idx, b_idx)
            improved = bullet_map.get(key, original_bullet)

            # Only accept if not empty and not wildly different length (>3x or <0.33x)
            if improved and improved != original_bullet and _is_reasonable_rewrite(original_bullet, improved):
                exp.bullets[b_idx] = improved
                changes.append(DiffEntry(
                    field=f"experience[{exp_idx}].bullets[{b_idx}]",
                    original=original_bullet,
                    updated=improved,
                ))
            else:
                exp.bullets[b_idx] = original_bullet  # Keep original if suspicious

    # ------------------------------------------------------------------ #
    # 3. Skills reordering
    # ------------------------------------------------------------------ #
    if ranked_skills and _skills_integrity_ok(resume.skills, ranked_skills):
        original_skills_str = ", ".join(resume.skills)
        tailored.skills     = ranked_skills
        new_skills_str      = ", ".join(ranked_skills)
        if original_skills_str != new_skills_str:
            changes.append(DiffEntry(
                field="skills",
                original=original_skills_str,
                updated=new_skills_str,
            ))
            logger.debug("Skills reordered: %d items", len(ranked_skills))
    else:
        logger.warning("Optimizer — skill integrity check failed; keeping original order.")

    logger.info(
        "Optimizer — done. %d changes tracked (summary=%s, bullets=%d, skills=%s)",
        len(changes),
        "yes" if any(c.field == "professional_summary" for c in changes) else "no",
        sum(1 for c in changes if "bullets" in c.field),
        "yes" if any(c.field == "skills" for c in changes) else "no",
    )

    return TailoredResume(
        match_score=analysis.match_score,
        original_resume=resume,
        tailored_resume=tailored,
        missing_skills=analysis.missing_skills,
        experience_gaps=analysis.experience_gaps,
        suggestions=analysis.suggestions,
        changes=changes,
        session_id=str(uuid.uuid4()),
    )


# ---------------------------------------------------------------------------
# Integrity helpers
# ---------------------------------------------------------------------------

def _is_reasonable_rewrite(original: str, improved: str) -> bool:
    """
    Sanity-check that a rewritten bullet is plausible.

    Rejects rewrites that:
    - Are empty
    - Are more than 4x longer than the original (likely hallucination)
    - Are less than 25% of the original length (important info dropped)
    """
    if not improved.strip():
        return False
    ratio = len(improved) / max(len(original), 1)
    return 0.25 <= ratio <= 4.0


def _skills_integrity_ok(original: list[str], ranked: list[str]) -> bool:
    """
    Ensure the ranked list contains exactly the same skills as the original.
    Comparison is case-insensitive.
    """
    if len(original) != len(ranked):
        return False
    orig_lower = {s.lower() for s in original}
    rank_lower = {s.lower() for s in ranked}
    return orig_lower == rank_lower
