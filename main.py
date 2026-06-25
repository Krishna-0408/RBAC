from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_current_user
from database import engine, get_db
from models import Base, User
from schemas import UserCreate, UserResponse
from schemas import UserCreate, UserResponse, LoginRequest, Token
from auth import (
    create_access_token,
    create_email_token,
    verify_email_token
)
from models import Item
from schemas import ItemCreate
from role_dependency import admin_required
from fastapi import BackgroundTasks
from email_utils import send_verification_mail, send_welcome_mail

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "FastAPI RBAC Project"}

from fastapi import BackgroundTasks

temp_users = {}

@app.post("/signup")
def signup(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    token = create_email_token(user.email)

    temp_users[user.email]={
        "email":user.email,
        "password":user.password,
        "role":user.role
    }

    background_tasks.add_task(
        send_verification_mail,
        user.email,
        token
    )

    return {
        "message":"Verification email sent"
    }

@app.get("/verify-email")
def verify_email(
    token: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    # Decode token
    email = verify_email_token(token)

    if email is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token"
        )

    # Check whether signup data exists
    if email not in temp_users:
        raise HTTPException(
            status_code=404,
            detail="User data not found. Please signup again."
        )

    data = temp_users[email]

    # Prevent duplicate users
    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        return {
            "message": "User already verified"
        }

    # Save user to database
    new_user = User(
        email=data["email"],
        password=data["password"],
        role=data["role"],
        is_verified=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send welcome email
    background_tasks.add_task(
        send_welcome_mail,
        data["email"],
        data["role"]
    )

    # Remove temporary data
    del temp_users[email]

    return {
        "message": "Email verified successfully"
    }

@app.post("/login", response_model=Token)
def login(user: LoginRequest,
          db: Session = Depends(get_db)):

    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email"
        )

    if db_user.password != user.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    access_token = create_access_token(
        data={
            "sub": db_user.email,
            "role": db_user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/profile")
def profile(current_user: User = Depends(get_current_user)):

    return {
        "email": current_user.email,
        "role": current_user.role
    }

@app.post("/logout")
def logout():

    return {
        "message": "Logged out successfully"
    }
@app.get("/items")
def get_items(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):

    items = db.query(Item).all()

    return items

@app.post("/items")
def create_item(
        item: ItemCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):

    new_item = Item(
        name=item.name,
        description=item.description
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item

@app.put("/items/{id}")
def update_item(
        id: int,
        item: ItemCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):

    db_item = db.query(Item).filter(
        Item.id == id
    ).first()

    if not db_item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    db_item.name = item.name
    db_item.description = item.description

    db.commit()

    return db_item

@app.delete("/items/{id}")
def delete_item(
        id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):

    db_item = db.query(Item).filter(
        Item.id == id
    ).first()

    if not db_item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    db.delete(db_item)
    db.commit()

    return {
        "message": "Deleted Successfully"
    }