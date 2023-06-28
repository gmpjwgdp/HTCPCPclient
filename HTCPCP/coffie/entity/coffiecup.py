from dataclasses import dataclass
@dataclass
class CoffieCup:
    temperature: int = 0
    water_level: int = 0
    caffeine_content: int = 0
    coffee_type: str = ""