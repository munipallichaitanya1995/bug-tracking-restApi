from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from database import get_db
from models import Project, ProjectMember, User as UserModel, UserRole
from schemas import Project as ProjectSchema, ProjectCreate, ProjectWithMembers, ProjectMemberCreate
from auth import get_current_user

router = APIRouter(prefix="/api/projects", tags=["projects"])

def check_project_access(project_id: str, user_id: str, db: Session):
    """Check if user has access to project."""
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    return membership

def check_maintainer_access(project_id: str, user_id: str, db: Session):
    """Check if user is a maintainer of the project."""
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
        ProjectMember.role == UserRole.maintainer
    ).first()
    return membership

@router.post("", response_model=ProjectSchema)
def create_project(
    project: ProjectCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project (current user becomes maintainer)."""
    # Check if key already exists
    existing_project = db.query(Project).filter(Project.key == project.key).first()
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project key already exists"
        )

    # Create project
    db_project = Project(
        name=project.name,
        key=project.key,
        description=project.description,
        creator_id=current_user.id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # Add creator as maintainer
    membership = ProjectMember(
        project_id=db_project.id,
        user_id=current_user.id,
        role=UserRole.maintainer
    )
    db.add(membership)

    # Add initial members if provided
    if project.initial_members:
        for email in project.initial_members:
            # Skip if it's the creator's email
            if email == current_user.email:
                continue

            # Find user by email
            user = db.query(UserModel).filter(UserModel.email == email).first()
            if user:
                # Check if already a member (shouldn't happen, but safety check)
                existing_membership = db.query(ProjectMember).filter(
                    ProjectMember.project_id == db_project.id,
                    ProjectMember.user_id == user.id
                ).first()
                if not existing_membership:
                    member_membership = ProjectMember(
                        project_id=db_project.id,
                        user_id=user.id,
                        role=UserRole.member
                    )
                    db.add(member_membership)

    db.commit()

    return db_project

@router.get("", response_model=List[ProjectSchema])
def get_projects(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all projects the current user belongs to."""
    projects = db.query(Project).join(ProjectMember).filter(
        ProjectMember.user_id == current_user.id
    ).all()
    return projects

@router.post("/{project_id}/members", response_model=dict)
def add_project_member(
    project_id: str,
    member: ProjectMemberCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a member to a project (maintainers only)."""
    # Check if current user is maintainer
    if not check_maintainer_access(project_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only maintainers can manage project members"
        )

    # Check if user exists
    user = db.query(UserModel).filter(UserModel.email == member.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if already a member
    existing_membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user.id
    ).first()
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this project"
        )

    # Add member
    membership = ProjectMember(
        project_id=project_id,
        user_id=user.id,
        role=member.role
    )
    db.add(membership)
    db.commit()

    return {"message": "Member added successfully"}

@router.get("/{project_id}/members", response_model=List[dict])
def get_project_members(
    project_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all members of a project."""
    # Check access
    if not check_project_access(project_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Join with User table to get user details in one query
    members = db.query(ProjectMember).join(UserModel).filter(
        ProjectMember.project_id == project_id
    ).all()

    result = []
    for member in members:
        result.append({
            "id": member.user_id,
            "name": member.user.name,
            "email": member.user.email,
            "role": member.role.value
        })

    return result
