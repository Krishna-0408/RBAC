from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Format:
# mysql+pymysql://username:password@host:port/database_name
DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/auth_db"

engine = create_engine(
    DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()