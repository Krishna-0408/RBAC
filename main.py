from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_current_user, blacklisted_tokens
from database import engine, get_db
from models import Base, User
from schemas import UserCreate, UserResponse
from schemas import UserCreate, UserResponse, LoginRequest, Token
from auth import create_access_token, get_password_hash, verify_password
from models import Item
from schemas import ItemCreate
from role_dependency import admin_required
from fastapi import BackgroundTasks
from email_utils import send_email
from schemas import ResetPassword

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "FastAPI RBAC Project"}


@app.post("/signup")
def signup(
        user: UserCreate,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        password=hashed_password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    background_tasks.add_task(
        send_email,
        user.email,
        user.role
    )

    return {
        "message": "User created successfully"
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



    if not verify_password(user.password, db_user.password):
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

from fastapi import Header

@app.post("/logout")
def logout(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    blacklisted_tokens.add(token)

    return {"message": "Logged out successfully"}
    
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

@app.post("/reset-password")
def reset_password(
    passwords: ResetPassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Verify current password
    if not verify_password(
        passwords.current_password,
        current_user.password
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )

    # Check new password and confirm password
    if passwords.new_password != passwords.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="New password and Confirm password do not match"
        )

    # Optional: Prevent using the same password
    if verify_password(passwords.new_password, current_user.password):
        raise HTTPException(
            status_code=400,
            detail="New password must be different from current password"
        )

    # Hash the new password
    current_user.password = get_password_hash(passwords.new_password)

    db.commit()

    return {
        "message": "Password changed successfully"
    }