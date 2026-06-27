"""
GET /api/download-pdf

Streams a PDF of the side-by-side comparison for a given TailoredResume.
"""

import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.models.tailored_resume import TailoredResume
from backend.services import pdf_generator

router = APIRouter()


@router.post(
    "/download-pdf",
    summary="Generate and download the tailored resume PDF",
    response_description="PDF file streamed as an attachment",
)
async def download_pdf(tailored_resume: TailoredResume):
    """
    Accept the full TailoredResume payload and return a PDF file as a streaming download.
    - Page 1: Match Score Summary, Missing Skills, Experience Gaps
    - Page 2+: Side-by-side Original vs Tailored resume with diff highlights
    """
    try:
        pdf_bytes = pdf_generator.generate(tailored_resume)
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=tailored_resume.pdf"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {str(e)}"
        )
