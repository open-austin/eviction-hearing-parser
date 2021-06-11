from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel


class EvictionHearing(BaseModel):
    """
    A hearing referenced in an eviction case docket.

    May be a future or past hearing.
    """

    hearing_date: str = ""
    hearing_time: str = ""
    hearing_officer: str = ""
    appeared: Optional[bool] = None
    hearing_type: str = ""
    all_text: str = ""
