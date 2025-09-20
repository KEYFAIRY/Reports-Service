import asyncio
from typing import List
import logging
from concurrent.futures import ThreadPoolExecutor
from app.domain.entities.musical_error import MusicalError
from app.domain.entities.postural_error import PosturalError
from app.domain.entities.practice import Practice
from app.domain.repositories.i_pdf_repo import IPDFRepo
from app.domain.repositories.i_video_repo import IVideoRepo

logger = logging.getLogger(__name__)

class PDFService:
    """Domain service for PDF generation and management"""

    def __init__(self, pdf_repo: IPDFRepo, video_repo: IVideoRepo):
        self.pdf_repo = pdf_repo
        self.video_repo = video_repo
        # Thread pool for CPU-intensive operations (video processing and PDF generation)
        self._executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="pdf_processing")

    async def generate_pdf(self, practice: Practice, postural_errors: List[PosturalError], musical_errors: List[MusicalError]) -> str:
        """Generate a PDF report for the given practice and errors."""
        logger.info(f"Generating PDF for practice {practice.id}")
        
        try:
            # Extract screenshots in thread pool (CPU-intensive with OpenCV)
            logger.debug(f"Starting screenshot extraction for practice_id={practice.id}")
            loop = asyncio.get_event_loop()
            screenshots = await loop.run_in_executor(
                self._executor,
                self._extract_screenshots_sync,
                practice.id_student,
                practice.id,
                postural_errors
            )
            logger.debug(f"Screenshot extraction completed for practice_id={practice.id}")
            
            # Generate PDF content in thread pool (CPU-intensive with ReportLab)
            logger.debug(f"Starting PDF generation for practice_id={practice.id}")
            pdf_content = await loop.run_in_executor(
                self._executor,
                self._generate_pdf_content_sync,
                practice,
                postural_errors,
                musical_errors,
                screenshots
            )
            logger.debug(f"PDF generation completed for practice_id={practice.id}")
            
            # Save PDF (I/O operation, keep async)
            filename = f"report_{practice.id}.pdf"
            pdf_path = await self.pdf_repo.save_pdf(practice.id_student, filename, pdf_content)
            
            logger.info(f"PDF generated successfully for practice {practice.id}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error generating PDF for practice {practice.id}: {e}", exc_info=True)
            raise
    
    def _extract_screenshots_sync(self, uid: str, practice_id: int, postural_errors: List[PosturalError]) -> dict:
        """Synchronous wrapper for screenshot extraction to run in thread pool."""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.video_repo.extract_screenshots_for_errors(uid, practice_id, postural_errors)
                )
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error extracting screenshots: {e}")
            return {}
    
    def _generate_pdf_content_sync(self, practice: Practice, postural_errors: List[PosturalError], musical_errors: List[MusicalError], screenshots: dict) -> bytes:
        """Synchronous wrapper for PDF content generation to run in thread pool."""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.pdf_repo.generate_pdf_content(practice, postural_errors, musical_errors, screenshots)
                )
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error generating PDF content: {e}")
            raise

    def __del__(self):
        """Cleanup del thread pool."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)