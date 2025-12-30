from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Comment
from schemas import Comment as CommentSchema, CommentCreate
from auth import get_current_user
from routers.projects import check_project_access

router = APIRouter(prefix="/api", tags=["comments"])

@router.get("/issues/{issue_id}/comments", response_model=List[CommentSchema])
def get_issue_comments(
    issue_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all comments for an issue."""
    # Check if issue exists and user has access
    from models import Issue
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    if not check_project_access(issue.project_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    comments = db.query(Comment).filter(Comment.issue_id == issue_id).order_by(Comment.created_at).all()
    return comments

@router.post("/issues/{issue_id}/comments", response_model=CommentSchema)
def create_comment(
    issue_id: str,
    comment: CommentCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new comment on an issue."""
    # Check if issue exists and user has access
    from models import Issue
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    if not check_project_access(issue.project_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Create comment
    db_comment = Comment(
        body=comment.body,
        issue_id=issue_id,
        author_id=current_user.id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment
