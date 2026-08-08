from dataclasses import dataclass

@dataclass
class SerialXData:
    scriptName: str
    scriptVersion: str
    commands: list