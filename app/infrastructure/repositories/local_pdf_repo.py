import os
import aiofiles
import logging
import tempfile
import shutil
from typing import List, Dict
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from app.domain.repositories.i_pdf_repo import IPDFRepo
from app.domain.entities.practice import Practice
from app.domain.entities.postural_error import PosturalError
from app.domain.entities.musical_error import MusicalError

logger = logging.getLogger(__name__)

class LocalPDFRepository(IPDFRepo):
    """Concrete implementation of IPDFRepo using local file system."""

    def __init__(self, base_dir: str | None = None):
        self.base_dir = base_dir or os.getenv("CONTAINER_VIDEO_PATH", "/app/storage")
        os.makedirs(self.base_dir, exist_ok=True)

    def _convert_mmss_to_seconds(self, mmss: str) -> float:
        """Convert mm:ss format to seconds."""
        try:
            if ':' in str(mmss):
                parts = str(mmss).split(':')
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            else:
                return float(mmss)
        except (ValueError, IndexError):
            return 0.0

    async def generate_pdf_content(
        self, 
        practice: Practice, 
        postural_errors: List[PosturalError], 
        musical_errors: List[MusicalError],
        screenshots: Dict[int, str]
    ) -> bytes:
        """Generate PDF content as bytes."""
        
        # Create temporary file with unique name for thread safety
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(temp_filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title = f"Reporte de practica: Escala {practice.scale}, {practice.scale_type}"
            elements.append(Paragraph(title, styles['Title']))
            elements.append(Spacer(1, 12))
            
            # Practice information
            info_text = f"""
            Fecha de la practica: {practice.date}<br/>
            Hora de la práctica: {practice.time}<br/>
            Duración del video: {practice.duration}<br/>
            BPM: {practice.bpm}<br/>
            Repeticiones: {practice.reps}<br/>
            Numero de errores posturales: {len(postural_errors)}<br/>
            Numero de errores Musicales: {len(musical_errors)}
            """
            elements.append(Paragraph(info_text, styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Postural errors section
            elements.append(Paragraph("Errores posturales:", styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            if postural_errors:
                postural_table_data = [["Inicio (mm:ss)", "Fin (mm:ss)", "Duración (s)", "Tipo de Error", "Pantallazo"]]
                
                for i, error in enumerate(postural_errors):
                    start_seconds = self._convert_mmss_to_seconds(error.min_sec_init)
                    end_seconds = self._convert_mmss_to_seconds(str(error.min_sec_end))
                    duration = end_seconds - start_seconds
                    
                    screenshot_path = screenshots.get(i)
                    
                    try:
                        if screenshot_path and os.path.exists(screenshot_path):
                            img = RLImage(screenshot_path)
                            img.drawHeight = 1.5 * inch
                            img.drawWidth = 2.2 * inch
                        else:
                            img = Paragraph("No disponible", styles['Normal'])
                    except Exception:
                        img = Paragraph("Error cargando imagen", styles['Normal'])
                    
                    postural_table_data.append([
                        error.min_sec_init,
                        str(error.min_sec_end),
                        f"{duration:.1f}",
                        Paragraph(error.explication, styles['Normal']),
                        img
                    ])
                
                postural_table = Table(postural_table_data, colWidths=[60, 60, 50, 180, 160], repeatRows=1)
                postural_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8)
                ]))
                
                elements.append(postural_table)
            else:
                elements.append(Paragraph("No se detectaron errores posturales.", styles['Normal']))
            
            elements.append(Spacer(1, 20))
            
            # Musical errors section
            elements.append(Paragraph("Errores musicales:", styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            if musical_errors:
                musical_table_data = [["Momento del error (mm:ss)", "Nota interpretada por el estudiante", "Nota correcta"]]
                
                for error in musical_errors:
                    musical_table_data.append([
                        error.min_sec,
                        error.note_played,
                        error.note_correct
                    ])
                
                musical_table = Table(musical_table_data, colWidths=[120, 150, 120], repeatRows=1)
                musical_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10)
                ]))
                
                elements.append(musical_table)
            else:
                elements.append(Paragraph("No se detectaron errores musicales.", styles['Normal']))
            
            # Build PDF
            doc.build(elements)
            
            # Read the generated PDF file
            with open(temp_filename, 'rb') as pdf_file:
                content = pdf_file.read()
            
            # Clean up temporary PDF file
            os.remove(temp_filename)
            
            # Clean up screenshot files
            for screenshot_path in screenshots.values():
                if screenshot_path and os.path.exists(screenshot_path):
                    try:
                        # Remove the screenshot file
                        os.remove(screenshot_path)
                        # Try to remove the parent directory if empty
                        parent_dir = os.path.dirname(screenshot_path)
                        if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                            os.rmdir(parent_dir)
                    except Exception as e:
                        logger.warning(f"Could not clean up screenshot {screenshot_path}: {e}")
            
            return content
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            raise e

    async def save_pdf(self, uid: str, filename: str, content: bytes) -> str:
        """Save PDF content and return the file path."""
        user_dir = os.path.join(self.base_dir, uid, "reports")
        os.makedirs(user_dir, exist_ok=True)
        file_path = os.path.join(user_dir, filename)

        try:
            async with aiofiles.open(file_path, "wb") as out_file:
                await out_file.write(content)
            logger.info(f"PDF saved at {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving PDF {filename}: {e}", exc_info=True)
            raise