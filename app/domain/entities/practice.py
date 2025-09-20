from dataclasses import dataclass
from typing import Optional

@dataclass
class Practice:
    id: int
    date: str
    time: str
    num_postural_errors: int
    num_musical_errors: int
    duration: int
    id_student: str
    student_name: str
    scale: str
    scale_type: str
    reps: int
    bpm: int