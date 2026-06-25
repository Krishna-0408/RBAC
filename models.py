from sqlalchemy import Column,Integer,String,Boolean
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    is_verified = Column(Boolean, default=False)

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(String(255))