from typing import Optional
from app.domain.entities.practice import Practice
from app.domain.repositories.i_practice_repo import IPracticeRepo


class PracticeService:
    def __init__(self, practice_repository: IPracticeRepo):
        self.practice_repository = practice_repository

    async def update_num_postural_errors(self, practice_id: int, num_errors: int) -> Optional[Practice]:
        return await self.practice_repository.update_num_postural_errors(practice_id, num_errors)
    
    async def update_num_musical_errors(self, practice_id: int, num_errors: int) -> Optional[Practice]:
        return await self.practice_repository.update_num_musical_errors(practice_id, num_errors)