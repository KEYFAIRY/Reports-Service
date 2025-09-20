from app.domain.repositories.i_video_repo import IVideoRepo


class VideoService:
    def __init__(self, video_repository: IVideoRepo):
        self.video_repository = video_repository

    async def get_video(self, uid: str, practice_id: int) -> str:
        return await self.video_repository.get_video(uid, practice_id)