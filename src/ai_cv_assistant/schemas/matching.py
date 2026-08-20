from enum import Enum
from pydantic import BaseModel,Field

class MatchStatus(str, Enum):
    STRONG_MATCH = "strong_match"
    PARTIAL_MATCH = "partial_match"
    NO_EVIDENCE = "no_evidence"
    CONFLICT = "conflict"

class MatchConfidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class MatchResult(BaseModel):
    requirement_id: str
    candidate_evidence_ids: list[str] = Field(default_factory=list)
    status: MatchStatus
    confidence: MatchConfidence

    reason: str

class MatchSummary(BaseModel):
    total_requirements: int = 0
    strong_matches: int = 0
    partial_matches: int = 0
    no_evidence: int = 0
    conflicts: int = 0

class CandidateJobMatch(BaseModel):
    results: list[MatchResult] = Field(default_factory=list)
    summary: MatchSummary = Field(default_factory=MatchSummary)
