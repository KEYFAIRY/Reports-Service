from dataclasses import dataclass
from typing import Optional

@dataclass
class PosturalError:
    id: int
    min_sec_init: str
    min_sec_end: str
    frame: int
    explication: str
    id_practice: int