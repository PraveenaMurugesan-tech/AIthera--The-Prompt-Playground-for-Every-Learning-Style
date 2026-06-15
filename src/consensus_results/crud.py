from typing import Optional
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.consensus_result import ConsensusResult


def create_consensus_result(
    db: Session,
    request_id: int,
    final_prompt: Optional[str] = None,
    quality_score: Optional[float] = None,
    consensus_reasoning: Optional[str] = None,
    combined_strengths: Optional[list[str]] = None,
    contributors: Optional[list[str]] = None,
    response_count: Optional[int] = None,
    metadata: Optional[dict] = None,
) -> ConsensusResult:
    """Create or return existing ConsensusResult for a PromptRequest."""

    existing = get_consensus_result(db=db, request_id=request_id)

    if existing:
        return existing

    result = ConsensusResult(
        request_id=request_id,
        final_prompt=final_prompt,
        quality_score=quality_score,
        consensus_reasoning=consensus_reasoning,
        combined_strengths=combined_strengths,
        contributors=contributors,
        response_count=response_count,
        response_metadata=metadata,
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    return result


def get_consensus_result(db: Session, request_id: int) -> Optional[ConsensusResult]:
    stmt = select(ConsensusResult).where(ConsensusResult.request_id == request_id)
    return db.execute(stmt).scalars().first()
