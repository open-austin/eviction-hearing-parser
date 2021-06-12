from datetime import date
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel, HttpUrl


class EvictionHearing(BaseModel):
    """
    A hearing referenced in an eviction case docket.

    May be a future or past hearing.
    """

    hearing_date: str = ""  # could become datetime.date
    hearing_time: str = ""  # could become datetime.time
    hearing_officer: str = ""
    appeared: Optional[bool] = None
    hearing_type: str = ""
    all_text: str = ""


class CaseEvent(BaseModel):
    case_event_date: Optional[date]
    served_date: str = ""
    served_subject: str = ""
    returned: str = ""


class EvictionCase(BaseModel):
    precinct_number: int
    style: str
    plaintiff: str
    active_or_inactive: str  # could become optional bool
    judgment_after_moratorium: str  # could become optional bool
    defendants: str
    attorneys_for_plaintiffs: str
    attorneys_for_defendants: str
    case_number: str
    defendant_zip: str
    plaintiff_zip: str
    hearings: List[EvictionHearing]
    status: str
    type: str
    register_url: Optional[HttpUrl]
    disposition_type: str
    disposition_amount: Optional[Decimal]
    disposition_date: str
    disposition_awarded_to: str
    disposition_awarded_against: str
    comments: str
    writ: Optional[CaseEvent]
    writ_of_possession_service: Optional[CaseEvent]
    writ_of_possession_requested: Optional[CaseEvent]
    writ_of_possession_sent_to_constable_office: Optional[CaseEvent]
    writ_returned_to_court: Optional[CaseEvent]
    judgement_for: str
    match_score: str
    date_filed: str
    defendant_address: str = ""
    defendant_race: str = ""
    defendant_gender: str = ""
