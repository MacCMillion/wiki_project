from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class RevisionXML():
    page_title: str
    page_id : int
    revision_id : int
    author_name : str
    length : int
    ts : datetime
    revision_hash : str
    author_id : int = -1
    minor : bool = False
    comment : str = False
    revert : bool = False
    registered: bool = False

@dataclass
class RevisionPywii():
    page_title: str
    page_id: int
    revision_id: int
    author_name: str
    length: int
    d_length: int
    ts: datetime
    revision_hash: str
    # author_id: int = -1
    minor: bool = False
    comment: str = False
    revert: Any = False
    # registered: bool = False





