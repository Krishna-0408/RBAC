from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User
from auth import verify_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)

# Add this
blacklisted_tokens = set()


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):

    # Add this
    if token in blacklisted_tokens:
        raise HTTPException(
            status_code=401,
            detail="Token has been revoked"
        )

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    email = payload.get("sub")

    user = db.query(User).filter(
        User.email == email
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user