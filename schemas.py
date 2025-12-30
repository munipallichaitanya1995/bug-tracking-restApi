from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import UserRole, IssueStatus, Priority

# User schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str  # UUID string
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserProfile(User):
    pass

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Project schemas
class ProjectBase(BaseModel):
    name: str
    key: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    initial_members: Optional[List[str]] = None  # List of email addresses

class Project(ProjectBase):
    id: str  # UUID string
    created_at: datetime
    creator_id: str  # UUID string

    class Config:
        from_attributes = True

class ProjectWithMembers(Project):
    members: List["ProjectMember"] = []

class ProjectMemberBase(BaseModel):
    user_id: str  # UUID string
    role: UserRole = UserRole.member

class ProjectMemberCreate(ProjectMemberBase):
    email: EmailStr

class ProjectMember(ProjectMemberBase):
    project_id: str  # UUID string
    user: User

    class Config:
        from_attributes = True

# Issue schemas
class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.medium

class IssueCreate(IssueBase):
    assignee_id: Optional[str] = None  # UUID string

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IssueStatus] = None
    priority: Optional[Priority] = None
    assignee_id: Optional[str] = None  # UUID string

class Issue(IssueBase):
    id: str  # UUID string
    status: IssueStatus
    project_id: str  # UUID string
    reporter_id: str  # UUID string
    assignee_id: Optional[str] = None  # UUID string
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IssueWithDetails(Issue):
    reporter: User
    assignee: Optional[User] = None
    comments_count: Optional[int] = None

# Comment schemas
class CommentBase(BaseModel):
    body: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: str  # UUID string
    issue_id: str  # UUID string
    author_id: str  # UUID string
    created_at: datetime
    author: User

    class Config:
        from_attributes = True

# Filter and search schemas
class IssueFilters(BaseModel):
    q: Optional[str] = None
    status: Optional[IssueStatus] = None
    priority: Optional[Priority] = None
    assignee: Optional[str] = None  # UUID string
    sort: Optional[str] = "created_at"
    order: Optional[str] = "desc"

# Response schemas
class ErrorResponse(BaseModel):
    error: dict

# Update forward references
ProjectWithMembers.update_forward_refs()
ProjectMember.update_forward_refs()
