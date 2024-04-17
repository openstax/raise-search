from typing import List, Optional
from pydantic import BaseModel


class HitSource(BaseModel):
    content_id: str
    section: str
    activity_name: str
    lesson_page: str
    lesson_page_type: str
    teacher_only: bool


class HitHighlight(BaseModel):
    visible_content: Optional[List[str]] = None
    lesson_page: Optional[List[str]] = None
    activity_name: Optional[List[str]] = None


class Hit(BaseModel):
    _index: str
    _id: str
    _score: float
    _source: HitSource
    highlight: Optional[HitHighlight]


class Hits(BaseModel):
    total: dict
    hits: List[Hit]
    max_score: Optional[float]


class SearchResults(BaseModel):
    took: int
    timed_out: bool
    _shards: dict
    hits: Hits
