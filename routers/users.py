from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import get_current_user, get_password_hash
from schemas import UserProfile, UserUpdate
from database import get_db
from models import User

router = APIRouter(prefix="/api", tags=["users"])

@router.get("/me", response_model=UserProfile)
def get_current_user_profile(current_user = Depends(get_current_user)):
    """Get current user profile."""
    return current_user

@router.put("/me", response_model=UserProfile)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    # Check if email is already taken by another user
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        if field != "password":  # password is handled above
            setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user
