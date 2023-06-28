from dataclasses import dataclass, field
@dataclass
class CoffiePot:
    temperature: int = 0
    water_level: int = 0
    caffeine_content: int = 0
    coffee_type: str = ""
    can_provide_additions: list[str] = field(default_factory=lambda: ["milk-type", "syrup-type"])
