from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import User as UserModel
from schemas import UserCreate, User, Token
from auth import authenticate_user, create_access_token, get_password_hash

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup", response_model=User)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account."""
    # Check if user already exists
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        name=user.name,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

@router.post("/login", response_model=Token)
def login(user_credentials: dict, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    email = user_credentials.get("email")
    password = user_credentials.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password required"
        )

    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout():
    """Logout endpoint (client-side token removal)."""
    return {"message": "Successfully logged out"}
