"""
JD Parser Service — Phase 2 Implementation

Extracts structured fields from raw job description text using regex
and keyword matching. Returns a structured JobDescription Pydantic object.
"""

import re
from typing import List, Set

from backend.models.job_description import JobDescription

# ---------------------------------------------------------------------------
# Tech keyword vocabulary (ATS-relevant terms)
# ---------------------------------------------------------------------------
TECH_KEYWORDS: Set[str] = {
    # Languages
    "python", "java", "javascript", "typescript", "golang", "go", "rust", "c++",
    "c#", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "bash",
    "shell", "powershell", "perl", "dart", "elixir",
    # Frontend
    "react", "angular", "vue", "svelte", "next.js", "nextjs", "nuxt", "gatsby",
    "html", "css", "sass", "scss", "tailwindcss", "tailwind", "bootstrap",
    "webpack", "vite", "rollup", "redux", "graphql", "rest", "restful",
    # Backend / Frameworks
    "fastapi", "django", "flask", "express", "node.js", "nodejs", "spring",
    "spring boot", "rails", "laravel", "gin", "echo", "fiber", "nestjs",
    "grpc", "soap", "websocket", "celery", "gunicorn", "uvicorn",
    # Databases
    "postgresql", "postgres", "mysql", "mongodb", "redis", "sqlite", "oracle",
    "dynamodb", "cassandra", "elasticsearch", "neo4j", "firestore", "bigquery",
    "snowflake", "supabase", "prisma", "sqlalchemy",
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "heroku", "digitalocean", "vercel",
    "netlify", "docker", "kubernetes", "k8s", "terraform", "ansible",
    "jenkins", "github actions", "circleci", "gitlab ci", "helm", "prometheus",
    "grafana", "nginx", "apache", "linux", "unix",
    # AI / ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "scikit-learn", "pandas", "numpy", "opencv", "nlp", "llm", "langchain",
    "hugging face", "openai", "transformers", "spark", "hadoop",
    # Tools / Practices
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "agile",
    "scrum", "kanban", "ci/cd", "devops", "microservices", "monorepo",
    "tdd", "bdd", "unit testing", "pytest", "jest", "selenium",
    # Mobile
    "ios", "android", "react native", "flutter", "xamarin",
    # Other
    "api", "sdk", "oauth", "jwt", "oidc", "saml", "kafka", "rabbitmq",
    "etl", "data pipeline", "data warehouse", "cloud native", "serverless",
}

# Patterns for extracting specific JD fields
EXPERIENCE_PATTERN = re.compile(
    r"(\d+\+?\s*(?:–|-|to)?\s*\d*\+?)\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp\.?)?|"
    r"(\d+\+?\s*(?:years?|yrs?))\s+(?:of\s+)?(?:hands[- ]on\s+)?experience",
    re.I,
)

REQUIRED_SECTION_RE = re.compile(
    r"(required|must\s+have|mandatory|essential|minimum\s+qualifications?|requirements?)\s*[:\-]?",
    re.I,
)

PREFERRED_SECTION_RE = re.compile(
    r"(preferred|nice[- ]to[- ]have|good\s+to\s+have|bonus|plus|advantageous|desired)\s*[:\-]?",
    re.I,
)

RESPONSIBILITY_SECTION_RE = re.compile(
    r"(responsibilities|duties|what\s+you['']?ll\s+do|role\s+overview|key\s+responsibilities|"
    r"what\s+you\s+will\s+do|job\s+duties|your\s+role)\s*[:\-]?",
    re.I,
)

ROLE_TITLE_PATTERNS = [
    re.compile(r"^(?:job\s+title|role|position|title)\s*[:\-]\s*(.+)$", re.I),
    re.compile(r"^(?:we(?:'re|\s+are)\s+(?:looking|hiring)\s+for\s+(?:a|an)\s+)(.+?)(?:\s+to|\s+who|$)", re.I),
    re.compile(r"^(?:join\s+us\s+as\s+(?:a|an)\s+)(.+?)(?:\s+at|\s*$)", re.I),
]

BULLET_RE = re.compile(r"^[•·▪▸►\-–—*]\s+")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(raw_text: str) -> JobDescription:
    """
    Parse raw job description text and return a structured JobDescription.

    Args:
        raw_text: Plain text of the job description

    Returns:
        JobDescription: Populated Pydantic model with extracted fields
    """
    lines = [line.rstrip() for line in raw_text.splitlines() if line.strip()]

    role_title       = _extract_role_title(lines)
    company          = _extract_company(raw_text)
    experience_req   = _extract_experience_requirement(raw_text)
    responsibilities = _extract_responsibilities(lines)
    required_skills  = _extract_required_skills(lines, raw_text)
    preferred_skills = _extract_preferred_skills(lines, raw_text)
    keywords         = _extract_keywords(raw_text, required_skills, preferred_skills)

    return JobDescription(
        role_title=role_title,
        company=company,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        responsibilities=responsibilities,
        experience_required=experience_req,
        keywords=keywords,
        raw_text=raw_text,
    )


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def _extract_role_title(lines: List[str]) -> str:
    """Extract the job title from the first few lines or explicit labels."""
    # Check first 5 lines for explicit role label
    for line in lines[:5]:
        for pattern in ROLE_TITLE_PATTERNS:
            m = pattern.match(line.strip())
            if m:
                return m.group(1).strip().rstrip(".")

    # Heuristic: first non-trivial line that looks like a title
    for line in lines[:8]:
        stripped = line.strip()
        # Skip very long lines (they're usually descriptions, not titles)
        if 4 < len(stripped) < 80 and not BULLET_RE.match(stripped):
            # Skip lines that are clearly section headers of the JD body
            if not RESPONSIBILITY_SECTION_RE.match(stripped):
                return stripped

    return lines[0].strip() if lines else "Unknown Role"


def _extract_company(raw_text: str) -> str | None:
    """Try to extract the company name from common patterns."""
    patterns = [
        re.compile(r"(?:at|@|with|company|employer)\s*[:\-]?\s*([A-Z][A-Za-z0-9\s&.,'-]{2,40}?)(?:\.|,|\n|$)", re.I),
        re.compile(r"^([A-Z][A-Za-z0-9\s&.'-]{2,40})\s+is\s+(?:looking|hiring|seeking)", re.M),
        re.compile(r"^(?:about\s+us\s*[:\-]?\s*)([A-Z][A-Za-z0-9\s&.'-]{2,40})", re.M | re.I),
    ]
    for p in patterns:
        m = p.search(raw_text)
        if m:
            candidate = m.group(1).strip().rstrip(".,")
            if 2 < len(candidate) < 60:
                return candidate
    return None


def _extract_experience_requirement(raw_text: str) -> str:
    """Extract the experience requirement string."""
    matches = EXPERIENCE_PATTERN.findall(raw_text)
    # findall returns tuple groups; flatten and pick first non-empty
    for match_tuple in matches:
        for part in match_tuple:
            if part:
                # Find the full context around this match
                m = re.search(re.escape(part) + r".{0,40}", raw_text, re.I)
                if m:
                    return m.group(0).strip().rstrip(".,;")
    return ""


def _get_sections(lines: List[str]) -> dict:
    """
    Split JD lines into labelled sections:
    responsibilities, required, preferred, other.
    """
    sections = {"responsibilities": [], "required": [], "preferred": [], "other": []}
    current = "other"

    for line in lines:
        stripped = line.strip()
        if RESPONSIBILITY_SECTION_RE.match(stripped):
            current = "responsibilities"
        elif REQUIRED_SECTION_RE.match(stripped):
            current = "required"
        elif PREFERRED_SECTION_RE.match(stripped):
            current = "preferred"
        else:
            sections[current].append(stripped)

    return sections


def _extract_responsibilities(lines: List[str]) -> List[str]:
    """Extract responsibility bullet points from the JD."""
    sections = _get_sections(lines)
    resp_lines = sections["responsibilities"]

    # If no dedicated responsibilities section found, extract bullet lines from full text
    if not resp_lines:
        resp_lines = lines

    responsibilities = []
    for line in resp_lines:
        stripped = line.strip()
        if BULLET_RE.match(stripped):
            text = BULLET_RE.sub("", stripped).strip()
            if len(text) > 15:
                responsibilities.append(text)

    # Deduplicate
    seen = set()
    unique = []
    for r in responsibilities:
        key = r.lower()
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique[:20]  # Cap at 20 items


def _extract_required_skills(lines: List[str], raw_text: str) -> List[str]:
    """Extract required technical skills."""
    sections = _get_sections(lines)
    target_lines = sections["required"] or lines

    # 1. Pull skills from dedicated required section bullets
    skills_from_bullets = _skills_from_bullet_lines(target_lines)

    # 2. Scan whole text for known tech keywords
    skills_from_keywords = _scan_tech_keywords(raw_text)

    # Merge: bullets first, then supplement with keyword scan
    combined = _merge_skill_lists(skills_from_bullets, skills_from_keywords)
    return combined[:25]


def _extract_preferred_skills(lines: List[str], raw_text: str) -> List[str]:
    """Extract preferred/nice-to-have technical skills."""
    sections = _get_sections(lines)
    target_lines = sections["preferred"]
    if not target_lines:
        return []

    return _skills_from_bullet_lines(target_lines)[:15]


def _skills_from_bullet_lines(lines: List[str]) -> List[str]:
    """Pull skill-like tokens from bullet point lines."""
    skills = []
    for line in lines:
        stripped = line.strip()
        if BULLET_RE.match(stripped):
            text = BULLET_RE.sub("", stripped).strip()
            # Split on common delimiters within a bullet
            parts = re.split(r"[,;/]", text)
            for part in parts:
                p = part.strip().rstrip(".")
                # Keep short tokens that look like skills (< 5 words)
                if 1 < len(p) < 60 and len(p.split()) <= 5:
                    skills.append(p)
        else:
            # Inline comma-separated skills e.g. "Python, FastAPI, Docker"
            if re.search(r",", stripped) and len(stripped) < 120:
                parts = [p.strip() for p in stripped.split(",")]
                for p in parts:
                    clean = p.rstrip(".")
                    if 1 < len(clean) < 40 and len(clean.split()) <= 4:
                        skills.append(clean)

    return _deduplicate(skills)


def _scan_tech_keywords(raw_text: str) -> List[str]:
    """
    Scan the full JD text for known tech keywords using word-boundary matching.
    Returns list of found keywords (title-cased for display).
    """
    text_lower = raw_text.lower()
    found = []
    for keyword in sorted(TECH_KEYWORDS):
        # Match whole word/phrase
        pattern = re.compile(r"\b" + re.escape(keyword) + r"\b", re.I)
        if pattern.search(text_lower):
            # Preserve original casing from text if possible
            m = pattern.search(raw_text)
            found.append(m.group(0) if m else keyword)

    return found


def _extract_keywords(raw_text: str, required: List[str], preferred: List[str]) -> List[str]:
    """
    Build the ATS keyword list: union of required + preferred skills +
    any additional tech terms found in the full text.
    """
    all_skills = set(s.lower() for s in required + preferred)

    # Add any tech keywords not already captured
    tech = _scan_tech_keywords(raw_text)
    extra = [t for t in tech if t.lower() not in all_skills]

    # Also extract domain-specific phrases
    domain_phrases = _extract_domain_phrases(raw_text)

    combined = required + preferred + extra + domain_phrases
    return _deduplicate(combined)[:40]


def _extract_domain_phrases(raw_text: str) -> List[str]:
    """Extract important multi-word phrases like 'distributed systems', 'system design'."""
    important_phrases = [
        "system design", "distributed systems", "high availability", "scalability",
        "microservices architecture", "event-driven", "cloud native", "data modeling",
        "api design", "code review", "cross-functional", "agile methodology",
        "test-driven development", "continuous integration", "continuous deployment",
        "machine learning", "natural language processing", "computer vision",
        "data structures", "algorithms", "object-oriented programming",
        "functional programming", "version control", "database design",
    ]
    text_lower = raw_text.lower()
    found = []
    for phrase in important_phrases:
        if phrase in text_lower:
            found.append(phrase.title())
    return found


def _merge_skill_lists(primary: List[str], secondary: List[str]) -> List[str]:
    """Merge two skill lists, deduplicating by lowercase key."""
    seen = set()
    result = []
    for skill in primary + secondary:
        key = skill.lower()
        if key not in seen:
            seen.add(key)
            result.append(skill)
    return result


def _deduplicate(items: List[str]) -> List[str]:
    """Remove duplicates from a list preserving order (case-insensitive)."""
    seen: Set[str] = set()
    result = []
    for item in items:
        key = item.lower().strip()
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result
