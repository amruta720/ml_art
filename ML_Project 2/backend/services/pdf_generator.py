"""PDF generation service for storybooks."""
import logging
from pathlib import Path
from typing import List
import io

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
    from reportlab.lib.colors import HexColor
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from models.schemas import StoryPanel

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generates PDF documents from storybook data."""

    def __init__(self):
        """Initialize the PDF generator."""
        if not REPORTLAB_AVAILABLE:
            logger.warning("ReportLab not installed. PDF generation will not work.")

    def generate_storybook_pdf(
        self,
        story_title: str,
        panels: List[StoryPanel],
        output_path: Path = None
    ) -> bytes:
        """
        Generate a PDF from storybook data.

        Args:
            story_title: Title of the storybook
            panels: List of story panels
            output_path: Optional file path to save PDF (if None, returns bytes)

        Returns:
            PDF as bytes
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "ReportLab not installed. Install with: pip install reportlab"
            )

        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Build PDF content
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        panel_title_style = ParagraphStyle(
            'PanelTitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        narration_style = ParagraphStyle(
            'Narration',
            parent=styles['Normal'],
            fontSize=12,
            textColor=HexColor('#2C3E50'),
            spaceAfter=10,
            leading=16,
            fontName='Helvetica'
        )

        dialogue_style = ParagraphStyle(
            'Dialogue',
            parent=styles['Normal'],
            fontSize=11,
            textColor=HexColor('#7F8C8D'),
            leftIndent=20,
            spaceAfter=8,
            fontName='Helvetica-Oblique'
        )

        # Add title
        story.append(Paragraph(story_title, title_style))
        story.append(Spacer(1, 0.3*inch))

        # Add each panel
        for i, panel in enumerate(panels):
            # Panel title
            if panel.title:
                story.append(Paragraph(f"{panel.panel_number}. {panel.title}", panel_title_style))

            # Panel image (if available and file exists)
            if panel.image_url:
                try:
                    # Extract filename from URL
                    image_filename = panel.image_url.split("/")[-1]
                    image_path = Path("static/images") / image_filename

                    if image_path.exists():
                        # Add image (scaled to fit page width)
                        img = RLImage(str(image_path), width=5*inch, height=5*inch)
                        story.append(img)
                        story.append(Spacer(1, 0.2*inch))
                except Exception as e:
                    logger.error(f"Error adding image to PDF: {e}")

            # Narration
            if panel.narration:
                story.append(Paragraph(panel.narration, narration_style))

            # Dialogues
            if panel.dialogues:
                for dialogue in panel.dialogues:
                    dialogue_text = f'<b>{dialogue.speaker}:</b> "{dialogue.text}"'
                    story.append(Paragraph(dialogue_text, dialogue_style))

            # Add page break between panels (except for last panel)
            if i < len(panels) - 1:
                story.append(PageBreak())

        # Build PDF
        doc.build(story)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        # Optionally save to file
        if output_path:
            output_path.write_bytes(pdf_bytes)
            logger.info(f"PDF saved to: {output_path}")

        return pdf_bytes


# Singleton instance
pdf_generator = PDFGenerator()
