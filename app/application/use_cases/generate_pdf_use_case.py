import logging
from app.application.dto.practice_data_dto import PracticeDataDTO
from app.domain.entities.practice import Practice
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
        metadata_service: MetadataPracticeService,
        postural_error_service: PosturalErrorService,
        musical_error_service: MusicalErrorService,
        practice_service: PracticeService,
        pdf_service: PDFService
    ):
        self.metadata_service = metadata_service
        self.postural_error_service = postural_error_service
        self.musical_error_service = musical_error_service
        self.practice_service = practice_service
        self.pdf_service = pdf_service
        

    async def execute(self, practice_data: PracticeDataDTO) -> str:
        # Check if audio and video analysis are done
        processing_done = await self.metadata_service.is_video_and_audio_done(practice_data.uid, practice_data.practice_id)
        logger.info(f"Audio and video processing done: {processing_done}")

        if processing_done:
            # 1. Get errors
            logger.info(f"Fetching errors for practice ID: {practice_data.practice_id}")
            postural_errors = await self.postural_error_service.get_errors_by_practice(practice_data.practice_id)
            logger.info(f"Found postural errors: {postural_errors}")
            
            logger.info(f"Fetching musical errors for practice ID: {practice_data.practice_id}")
            musical_errors = await self.musical_error_service.get_errors_by_practice(practice_data.practice_id)
            logger.info(f"Found musical errors: {musical_errors}")
            
            # 2. Update Practice Data (number of errors)
            logger.info(f"Updating practice data for practice ID: {practice_data.practice_id}")
            practice_with_postural_updated = await self.practice_service.update_num_postural_errors(practice_data.practice_id, len(postural_errors))
            practice_with_musical_updated= await self.practice_service.update_num_musical_errors(practice_data.practice_id, len(musical_errors))
            logger.info("PRACTICE OF STUDENT: " + practice_with_postural_updated.student_name)
            logger.info(f"Updated practice data with {practice_with_postural_updated.num_postural_errors} postural errors.")
            logger.info(f"Updated practice data with {practice_with_musical_updated.num_musical_errors} musical errors.")
            
            # 3. Generate PDF
            if len(postural_errors) > 0 or len(musical_errors) > 0:
                
                practice = Practice(
                id=practice_with_postural_updated.id,
                date=practice_with_postural_updated.date,
                time=practice_with_postural_updated.time,
                num_postural_errors=practice_with_postural_updated.num_postural_errors,
                num_musical_errors=practice_with_musical_updated.num_musical_errors,
                duration=practice_with_postural_updated.duration,
                id_student=practice_with_postural_updated.id_student,
                student_name=practice_with_postural_updated.student_name,
                scale=practice_data.scale,
                scale_type=practice_data.scale_type,
                bpm=practice_data.bpm,
                figure=practice_data.figure,
                octaves=practice_data.octaves
                )
            
                logger.info(f"Generating PDF for practice {practice_data.practice_id}")
                pdf_path = await self.pdf_service.generate_pdf(practice, postural_errors, musical_errors)
                logger.info(f"PDF generated at path: {pdf_path}")
                
                logger.info(f"Saving PDF path to metadata for practice {practice.id}")
                await self.metadata_service.save_pdf_path(practice.id_student, practice.id, pdf_path)
                logger.info(f"PDF path saved successfully for practice {practice.id}")
                
                return pdf_path
            
            return ""
            
        else:
            error_msg = f"Audio and video processing not completed for practice ID: {practice_data.practice_id}"
            logger.error(error_msg)
            raise Exception(error_msg)