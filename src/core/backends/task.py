from dataclasses import dataclass
from typing import Tuple


class TaskException(Exception):
    pass


@dataclass
class Task:
    league: str
    want: str
    have: str
    limit: int
    poeofficial: bool
