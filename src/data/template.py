from dataclasses import dataclass

@dataclass
class Template:
    name: str
    wait: int
    encoded_config: str
    html: str = None

    def __str__(self):
        return f"{self.name} (wait: {self.wait})"