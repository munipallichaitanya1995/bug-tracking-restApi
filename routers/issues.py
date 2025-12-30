from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from typing import List, Optional
from database import get_db
from models import Issue, Project, User as UserModel, IssueStatus, Priority, UserRole
from schemas import Issue as IssueSchema, IssueCreate, IssueUpdate, IssueWithDetails, IssueFilters
from auth import get_current_user
from routers.projects import check_project_access, check_maintainer_access

router = APIRouter(prefix="/api", tags=["issues"])

def apply_filters(query, filters: IssueFilters):
    """Apply filters to issue query."""
    if filters.q:
        search_term = f"%{filters.q}%"
        query = query.filter(
            or_(
                Issue.title.ilike(search_term),
                Issue.description.ilike(search_term)
            )
        )

    if filters.status:
        query = query.filter(Issue.status == filters.status)

    if filters.priority:
        query = query.filter(Issue.priority == filters.priority)

    if filters.assignee:
        query = query.filter(Issue.assignee_id == filters.assignee)

    # Sorting
    sort_field = filters.sort or "created_at"
    sort_order = filters.order or "desc"

    if sort_field == "priority":
        # Custom sorting for priority enum
        priority_order = {
            Priority.low: 1,
            Priority.medium: 2,
            Priority.high: 3,
            Priority.critical: 4
        }
        if sort_order == "asc":
            query = query.order_by(
                asc(Issue.priority),
                desc(Issue.created_at)
            )
        else:
            query = query.order_by(
                desc(Issue.priority),
                desc(Issue.created_at)
            )
    elif sort_field == "status":
        if sort_order == "asc":
            query = query.order_by(asc(Issue.status), desc(Issue.created_at))
        else:
            query = query.order_by(desc(Issue.status), desc(Issue.created_at))
    else:
        # Default sorting by created_at
        if sort_order == "asc":
            query = query.order_by(asc(Issue.created_at))
        else:
            query = query.order_by(desc(Issue.created_at))

    return query

@router.get("/issues/{issue_id}", response_model=IssueWithDetails)
def get_issue(
    issue_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific issue with details."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    # Check access
    if not check_project_access(issue.project_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Get comments count
    from models import Comment
    comments_count = db.query(Comment).filter(Comment.issue_id == issue_id).count()

    issue_dict = IssueWithDetails.from_orm(issue).__dict__
    issue_dict["comments_count"] = comments_count
    return IssueWithDetails(**issue_dict)

@router.patch("/issues/{issue_id}", response_model=IssueSchema)
def update_issue(
    issue_id: str,
    issue_update: IssueUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an issue (maintainers can update status/assignee, reporters can update other fields)."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    # Check access
    if not check_project_access(issue.project_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Check permissions for status/assignee changes
    is_maintainer = check_maintainer_access(issue.project_id, current_user.id, db)
    if (issue_update.status is not None or issue_update.assignee_id is not None) and not is_maintainer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only maintainers can update status and assignee"
        )

    # Check if assignee is a project member
    if issue_update.assignee_id:
        from models import ProjectMember
        assignee_membership = db.query(ProjectMember).filter(
            ProjectMember.project_id == issue.project_id,
            ProjectMember.user_id == issue_update.assignee_id
        ).first()
        if not assignee_membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee must be a project member"
            )

    # Update issue
    update_data = issue_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(issue, field, value)

    db.commit()
    db.refresh(issue)
    return issue

@router.delete("/issues/{issue_id}")
def delete_issue(
    issue_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an issue (maintainers only)."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    # Check maintainer access
    if not check_maintainer_access(issue.project_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only maintainers can delete issues"
        )

    db.delete(issue)
    db.commit()
    return {"message": "Issue deleted successfully"}

@router.get("/projects/{project_id}/issues", response_model=List[IssueWithDetails])
def get_project_issues(
    project_id: str,
    q: Optional[str] = None,
    status: Optional[IssueStatus] = None,
    priority: Optional[Priority] = None,
    assignee: Optional[str] = None,
    sort: Optional[str] = "created_at",
    order: Optional[str] = "desc",
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get issues for a project with filtering and sorting."""
    # Check access
    if not check_project_access(project_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Build filters
    filters = IssueFilters(
        q=q, status=status, priority=priority,
        assignee=assignee, sort=sort, order=order
    )

    # Query issues
    query = db.query(Issue).filter(Issue.project_id == project_id)
    query = apply_filters(query, filters)
    issues = query.all()

    # Add details
    result = []
    for issue in issues:
        issue_dict = IssueWithDetails.from_orm(issue).__dict__
        # Add comments count
        from models import Comment
        comments_count = db.query(Comment).filter(Comment.issue_id == issue.id).count()
        issue_dict["comments_count"] = comments_count
        result.append(IssueWithDetails(**issue_dict))

    return result

@router.post("/projects/{project_id}/issues", response_model=IssueSchema)
def create_issue(
    project_id: str,
    issue: IssueCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new issue in a project."""
    # Check access
    if not check_project_access(project_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Check if assignee is a project member (if specified)
    if issue.assignee_id:
        from models import ProjectMember
        assignee_membership = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == issue.assignee_id
        ).first()
        if not assignee_membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee must be a project member"
            )

    # Create issue
    db_issue = Issue(
        title=issue.title,
        description=issue.description,
        priority=issue.priority,
        project_id=project_id,
        reporter_id=current_user.id,
        assignee_id=issue.assignee_id
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue
