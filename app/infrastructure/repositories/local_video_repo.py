import logging
import os
import cv2
import tempfile
from typing import List, Dict
from app.domain.repositories.i_video_repo import IVideoRepo
from app.domain.entities.postural_error import PosturalError

logger = logging.getLogger(__name__)

class LocalVideoRepository(IVideoRepo):
    """Concrete implementation of IVideoRepo using local filesystem."""
    
    def __init__(self, base_dir: str | None = None):
        self.base_dir = base_dir or os.getenv("CONTAINER_VIDEO_PATH", "/app/storage")

    async def get_video(self, uid: str, practice_id: int) -> str:
        """Retrieve the video file path for the given practice ID."""
        return self.base_dir + f"/{uid}/videos/practice_{practice_id}.mp4"

    def _parse_timestamp(self, timestamp: str) -> float:
        """Helper method to parse mm:ss format to seconds."""
        try:
            if ':' in str(timestamp):
                parts = str(timestamp).split(':')
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            else:
                return float(timestamp)
        except (ValueError, IndexError):
            return 0.0

    async def extract_screenshots_for_errors(self, uid: str, practice_id: int, postural_errors: List[PosturalError]) -> Dict[int, str]:
        """Extract screenshots for postural errors and return a mapping of error index to screenshot path."""
        screenshots = {}
        
        if not postural_errors:
            return screenshots
        
        # Get video path using the repository's own method
        video_path = await self.get_video(uid, practice_id)
        
        # Create temporary directory with unique name for thread safety
        temp_dir = tempfile.mkdtemp(prefix=f"screenshots_{practice_id}_")
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Could not open video: {video_path}")
                return screenshots
            
            for i, error in enumerate(postural_errors):
                # Parse timestamps and calculate middle point
                start_seconds = self._parse_timestamp(error.min_sec_init)
                end_seconds = self._parse_timestamp(error.min_sec_end)
                middle_timestamp = (start_seconds + end_seconds) / 2
                
                # Set video position to the desired timestamp
                cap.set(cv2.CAP_PROP_POS_MSEC, middle_timestamp * 1000)
                ret, frame = cap.read()
                
                if ret:
                    screenshot_path = os.path.join(temp_dir, f"error_{practice_id}_{i}.png")
                    cv2.imwrite(screenshot_path, frame)
                    screenshots[i] = screenshot_path
                    logger.debug(f"Screenshot extracted for error {i} at {middle_timestamp}s")
                else:
                    logger.warning(f"Could not extract frame at {middle_timestamp}s for error {i}")
                    screenshots[i] = None
            
            cap.release()
            logger.info(f"Extracted {len(screenshots)} screenshots from video")
            
        except Exception as e:
            logger.error(f"Error extracting screenshots: {e}")
            # Clean up temp directory on error
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
            
        return screenshots