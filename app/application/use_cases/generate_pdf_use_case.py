import logging
from app.application.dto.practice_data_dto import PracticeDataDTO
from app.domain.services.metadata_service import MetadataPracticeService
from app.domain.services.musical_error_service import MusicalErrorService
from app.domain.services.pdf_service import PDFService
from app.domain.services.postural_error_service import PosturalErrorService
from app.domain.services.practice_service import PracticeService
from app.domain.services.video_service import VideoService

logger = logging.getLogger(__name__)

class GeneratePDFUseCase:
    def __init__(
        self,
        practice_service: PracticeService,
        postural_error_service: PosturalErrorService,
        musical_error_service: MusicalErrorService,
        metadata_service: MetadataPracticeService,
        video_service: VideoService,
        pdf_service: PDFService,
    ):
        self.practice_service = practice_service
        self.postural_error_service = postural_error_service
        self.musical_error_service = musical_error_service
        self.metadata_service = metadata_service
        self.video_service = video_service
        self.pdf_service = pdf_service

    async def execute(self, practice_data: PracticeDataDTO) -> str:
        # Check if audio and video analysis are done
        if not self.metadata_service.is_video_and_audio_done(practice_data.uid, practice_data.practice_id):
            raise Exception(f"Audio analysis not completed for practice {practice_data.practice_id}")
        
        # 1. Fetch errors
        logger.info(f"Getting errors for practice {practice_data.practice_id}")
        postural_errors = await self.postural_error_service.get_errors_by_practice(practice_data.practice_id)
        musical_errors = await self.musical_error_service.get_errors_by_practice(practice_data.practice_id)
        
        # 2. Generate PDF (no need to get video separately, PDF service handles it)
        logger.info(f"Generating PDF for practice {practice_data.practice_id}")
        pdf_path = await self.pdf_service.generate_pdf(
            practice=practice_data,
            postural_errors=postural_errors,
            musical_errors=musical_errors
        )
        
        # 3. Update metadata
        logger.info(f"Saving PDF path to metadata for practice {practice_data.practice_id}")
        await self.metadata_service.save_pdf_path(practice_data.practice_id, pdf_path)
        
        # 4. Update practice
        logger.info(f"Updating practice {practice_data.practice_id} with error counts")
        await self.practice_service.update_num_musical_errors(practice_data.practice_id, len(musical_errors))
        await self.practice_service.update_num_postural_errors(practice_data.practice_id, len(postural_errors))
        
        logger.info(f"PDF generation completed for practice {practice_data.practice_id}")
        
        return pdf_path