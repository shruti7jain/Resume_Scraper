"""
PDF Generation Service
Phase 5 Implementation

Renders a side-by-side comparison PDF using WeasyPrint and Jinja2.
"""
import os
from jinja2 import Environment, FileSystemLoader
from backend.models.tailored_resume import TailoredResume

# Path to the templates directory relative to this file
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

def generate(tailored_resume: TailoredResume) -> bytes:
    """
    Generate a downloadable PDF from the TailoredResume using xhtml2pdf.

    Returns raw PDF bytes to be streamed as a FastAPI response.
    """
    import io
    try:
        from xhtml2pdf import pisa
    except ImportError as e:
        raise RuntimeError(
            "xhtml2pdf is not installed. Please install it using 'pip install xhtml2pdf'."
        ) from e

    # Load Jinja2 template
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("pdf_template.html")
    
    # Render HTML with data
    rendered_html = template.render(data=tailored_resume)
    
    # Generate PDF
    dest = io.BytesIO()
    pisa_status = pisa.CreatePDF(
        rendered_html,
        dest=dest
    )
    
    if pisa_status.err:
        raise RuntimeError("PDF generation failed using xhtml2pdf.")
    
    return dest.getvalue()
