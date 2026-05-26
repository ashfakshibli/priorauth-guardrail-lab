from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ReviewQueueItem
from app.schemas import ReviewQueueItemOut

router = APIRouter(prefix="/api/review-queue", tags=["queue"])


@router.get("", response_model=list[ReviewQueueItemOut])
def get_review_queue(db: Session = Depends(get_db)):
    items = (
        db.query(ReviewQueueItem)
        .filter(ReviewQueueItem.resolved == False)  # noqa: E712
        .order_by(ReviewQueueItem.created_at.desc())
        .all()
    )
    return items
