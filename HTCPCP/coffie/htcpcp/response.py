from typing import Optional
from dataclasses import dataclass

@dataclass
class HTCPCPResponse:
    status_code: int = 200
    content_type: Optional[str] = "text/html; charset=UTF-8"
    body: bytes = b""