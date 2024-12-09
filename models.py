from pydantic import BaseModel
from typing import List, Optional

class Backend(BaseModel):
    id: int
    url: str
    alias: Optional[str] = None

class Group(BaseModel):
    id: int
    path: str
    alias: Optional[str] = None
    health_check_path: str
    backends: List[Backend] = []
    current_backend: Optional[Backend] = None 