from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from mercurius import Mercurius


DATABASE_URL = "sqlite:///./example.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    value = Column(Integer, index=True)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ItemCreate(BaseModel):
    name: str
    value: int


class ItemRead(BaseModel):
    id: int
    name: str
    value: int

    class Config:
        orm_mode = True


class ItemUpdate(BaseModel):
    name: str | None = None
    value: int | None = None


def require_auth(token: str = "fake-token"):
    if token != "fake-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


app = FastAPI(title="Mercurius example")

Mercurius(
    app,
    Item,
    ItemRead,
    get_db,
    create_schema=ItemCreate,
    update_schema=ItemUpdate,
    operation_dependencies={"create": [require_auth]},
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
