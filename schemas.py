from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str
    role: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str




class ItemCreate(BaseModel):
    name: str
    description: str


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True



class ResetPassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str