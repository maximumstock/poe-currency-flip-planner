from dataclasses import dataclass


class TaskException(Exception):
    status_code: int

    def __init__(self, status_code: int):
        self.status_code = status_code


@dataclass
class Task:
    league: str
    want: str
    have: str
    limit: int
    poeofficial: bool
