#!/usr/bin/env python3
"""
Seed script to populate the database with demo data.
Run with: python seed.py
"""
import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Project, ProjectMember, Issue, Comment, UserRole, IssueStatus, Priority
import bcrypt

def get_password_hash(password):
    """Hash a password for seeding."""
    password = password.encode('utf-8')
    if len(password) > 72:
        password = password[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password, salt).decode('utf-8')

def seed_database():
    """Seed the database with demo data."""
    # Drop all tables first to ensure clean schema
    Base.metadata.drop_all(bind=engine)
    # Create tables with correct schema
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(User).first():
            print("Database already seeded. Skipping...")
            return

        # Create demo users
        users_data = [
            {"name": "Alice Johnson", "email": "alice@example.com", "password": "pass123"},
            {"name": "Bob Smith", "email": "bob@example.com", "password": "pass123"},
            {"name": "Carol Williams", "email": "carol@example.com", "password": "pass123"},
            {"name": "David Brown", "email": "david@example.com", "password": "pass123"},
        ]

        # Create users with specific UUIDs for demo purposes
        user_uuids = [
            "550e8400-e29b-41d4-a716-446655440000",  # Alice
            "550e8400-e29b-41d4-a716-446655440001",  # Bob
            "550e8400-e29b-41d4-a716-446655440002",  # Carol
            "550e8400-e29b-41d4-a716-446655440003",  # David
        ]

        users = []
        for i, user_data in enumerate(users_data):
            user = User(
                id=user_uuids[i],
                name=user_data["name"],
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"])
            )
            db.add(user)
            users.append(user)

        db.commit()

        # Create demo projects
        projects_data = [
            {"name": "IssueHub Web App", "key": "IHUB", "description": "Main web application for issue tracking"},
            {"name": "Mobile App", "key": "MOBILE", "description": "Mobile application for issue tracking"},
        ]

        projects = []
        for project_data in projects_data:
            project = Project(
                name=project_data["name"],
                key=project_data["key"],
                description=project_data["description"],
                creator_id=users[0].id  # Alice is creator
            )
            db.add(project)
            projects.append(project)

        db.commit()
        for project in projects:
            db.refresh(project)

        # Add project members
        memberships = [
            # IssueHub Web App - Alice (maintainer), Bob and Carol (members)
            ProjectMember(project_id=projects[0].id, user_id=users[0].id, role=UserRole.maintainer),
            ProjectMember(project_id=projects[0].id, user_id=users[1].id, role=UserRole.member),
            ProjectMember(project_id=projects[0].id, user_id=users[2].id, role=UserRole.member),

            # Mobile App - Carol (maintainer), David (member)
            ProjectMember(project_id=projects[1].id, user_id=users[2].id, role=UserRole.maintainer),
            ProjectMember(project_id=projects[1].id, user_id=users[3].id, role=UserRole.member),
        ]

        for membership in memberships:
            db.add(membership)
        db.commit()

        # Create demo issues
        issues_data = [
            {
                "title": "Implement user authentication",
                "description": "Add JWT-based authentication system with signup, login, and logout",
                "status": IssueStatus.resolved,
                "priority": Priority.high,
                "project_id": projects[0].id,
                "reporter_id": users[0].id,
                "assignee_id": users[1].id,
            },
            {
                "title": "Create project management API",
                "description": "Build REST API endpoints for project CRUD operations",
                "status": IssueStatus.resolved,
                "priority": Priority.high,
                "project_id": projects[0].id,
                "reporter_id": users[0].id,
                "assignee_id": users[2].id,
            },
            {
                "title": "Design responsive UI",
                "description": "Create a clean, responsive user interface using Tailwind CSS",
                "status": IssueStatus.in_progress,
                "priority": Priority.medium,
                "project_id": projects[0].id,
                "reporter_id": users[1].id,
                "assignee_id": users[0].id,
            },
            {
                "title": "Add issue filtering and search",
                "description": "Implement advanced filtering by status, priority, assignee, and text search",
                "status": IssueStatus.open,
                "priority": Priority.medium,
                "project_id": projects[0].id,
                "reporter_id": users[2].id,
            },
            {
                "title": "Implement push notifications",
                "description": "Add push notifications for issue updates and mentions",
                "status": IssueStatus.open,
                "priority": Priority.low,
                "project_id": projects[1].id,
                "reporter_id": users[2].id,
                "assignee_id": users[3].id,
            },
            {
                "title": "Fix mobile layout issues",
                "description": "Resolve responsive design problems on mobile devices",
                "status": IssueStatus.in_progress,
                "priority": Priority.high,
                "project_id": projects[1].id,
                "reporter_id": users[3].id,
                "assignee_id": users[2].id,
            },
        ]

        issues = []
        for issue_data in issues_data:
            issue = Issue(**issue_data)
            db.add(issue)
            issues.append(issue)

        db.commit()
        for issue in issues:
            db.refresh(issue)

        # Create demo comments
        comments_data = [
            {
                "body": "Authentication system is now complete with JWT tokens and password hashing.",
                "issue_id": issues[0].id,
                "author_id": users[1].id,
            },
            {
                "body": "API endpoints are working correctly. All CRUD operations implemented.",
                "issue_id": issues[1].id,
                "author_id": users[2].id,
            },
            {
                "body": "Started working on the responsive design. Will use Tailwind CSS for styling.",
                "issue_id": issues[2].id,
                "author_id": users[0].id,
            },
            {
                "body": "This is a great feature request! Filtering will really improve usability.",
                "issue_id": issues[3].id,
                "author_id": users[0].id,
            },
            {
                "body": "Need to check if this works on iOS Safari as well.",
                "issue_id": issues[5].id,
                "author_id": users[2].id,
            },
        ]

        for comment_data in comments_data:
            comment = Comment(**comment_data)
            db.add(comment)

        db.commit()

        print("Database seeded successfully!")
        print("\nDemo users:")
        for user in users_data:
            print(f"- {user['name']} ({user['email']}) - Password: {user['password']}")

        print("\nDemo projects created:")
        for project in projects_data:
            print(f"- {project['name']} ({project['key']})")

        print(f"\nTotal issues created: {len(issues)}")
        print(f"Total comments created: {len(comments_data)}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
