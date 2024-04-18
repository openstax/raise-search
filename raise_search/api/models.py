from typing import List, Optional
from pydantic import BaseModel, Field


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
    index: str = Field(..., alias="_index")
    id: str = Field(..., alias="_id")
    score: float = Field(..., alias="_score")
    source: HitSource = Field(..., alias="_source")
    highlight: Optional[HitHighlight]


class HitTotal(BaseModel):
    value: int
    relation: str


class Hits(BaseModel):
    total: HitTotal
    hits: List[Hit]
    max_score: Optional[float]


class ShardData(BaseModel):
    total: int
    successful: int
    skipped: int
    failed: int


class SearchResults(BaseModel):
    took: int
    timed_out: bool
    shards: ShardData = Field(..., alias="_shards")
    hits: Hits
