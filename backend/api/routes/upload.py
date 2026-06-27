"""
POST /api/upload-resume

Accepts a PDF or DOCX resume file upload and returns a structured Resume JSON.
Phase 2: Wired to resume_parser service.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from backend.models.resume import Resume
from backend.services import resume_parser

router = APIRouter()

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


@router.post("/upload-resume", response_model=Resume, summary="Upload and parse a resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a PDF or DOCX resume.

    - Validates file type (PDF / DOCX) and size (≤ 5 MB)
    - Parses the file using `resume_parser` (pdfplumber / python-docx)
    - Returns a structured `Resume` JSON with all extracted fields
    """
    # --- Validate content type ---
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=(
                f"Unsupported file type '{file.content_type}'. "
                "Only PDF (.pdf) and Word (.docx) files are accepted."
            ),
        )

    # --- Read and validate size ---
    content = await file.read()
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds the 5 MB limit. Got {len(content) / 1024 / 1024:.2f} MB.",
        )

    # --- Parse resume ---
    try:
        parsed_resume = resume_parser.parse(content, file.content_type)
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to parse resume: {str(exc)}",
        ) from exc

    return parsed_resume
