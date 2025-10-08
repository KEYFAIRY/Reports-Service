from dataclasses import dataclass
from typing import Optional

@dataclass
class MusicalError:
    id: int
    min_sec: str
    note_played: str
    note_correct: str
    id_practice: int