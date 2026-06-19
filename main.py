from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_current_user
from database import engine, get_db
from models import Base, User
from schemas import UserCreate, UserResponse
from schemas import UserCreate, UserResponse, LoginRequest, Token
from auth import create_access_token
from models import Item
from schemas import ItemCreate
from role_dependency import admin_required

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "FastAPI RBAC Project"}


@app.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
        email=user.email,
        password=user.password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

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