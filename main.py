from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, users, projects, issues, comments
from models import Base
from database import engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IssueHub API",
    description="A lightweight bug tracking system",
    version="1.0.1"  # Force reload
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev server ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(issues.router)
app.include_router(comments.router)

@app.get("/")
def read_root():
    return {"message": "IssueHub API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
