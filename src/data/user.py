from dataclasses import dataclass

@dataclass
class User:
    args: dict
    page_id: str = None