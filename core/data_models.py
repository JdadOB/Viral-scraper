from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Platform(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"


class VideoItem(BaseModel):
    id: str
    platform: Platform
    url: str
    author: str
    description: str
    thumbnail_url: str = ""
    play_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    save_count: int = 0
    view_count: int = 0
    duration_seconds: float = 0.0
    hashtags: list[str] = Field(default_factory=list)
    sound_name: str = ""
    sound_duration_days: int = 0
    posted_at: Optional[datetime] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    virality_score: float = 0.0
    raw_data: dict = Field(default_factory=dict)


class ScraperResult(BaseModel):
    platform: Platform
    query: str
    items: list[VideoItem] = Field(default_factory=list)
    total_count: int = 0
    success: bool = True
    error_message: str = ""
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
