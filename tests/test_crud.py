import os
import sys

from fastapi import FastAPI, HTTPException
from typing import Optional
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Any
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(bind=ENGINE)
Base: Any = declarative_base()


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    value = Column(Integer, index=True)


Base.metadata.create_all(bind=ENGINE)


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
    name: Optional[str] = None  
    value: Optional[int] = None


def create_app(operation_deps=None):
    app = FastAPI()
    try:
        from mercurius import Mercurius
    except Exception:
        ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        from mercurius import Mercurius

    Mercurius(
        app,
        Item,
        ItemRead,
        get_db,
        create_schema=ItemCreate,
        update_schema=ItemUpdate,
        operation_dependencies=operation_deps,
    )
    return app


def test_crud_basic():
    app = create_app()
    client = TestClient(app)

    r = client.post("/items/", json={"name": "a", "value": 10})
    assert r.status_code == 201
    obj = r.json()
    assert obj["name"] == "a"
    id1 = obj["id"]

    r = client.post("/items/", json={"name": "b", "value": 5})
    assert r.status_code == 201

    r = client.get("/items/")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 2

    r = client.get(f"/items/{id1}")
    assert r.status_code == 200
    assert r.json()["name"] == "a"

    r = client.put(f"/items/{id1}", json={"value": 20})
    assert r.status_code == 200
    assert r.json()["value"] == 20

    r = client.delete(f"/items/{id1}")
    assert r.status_code == 204


def test_pagination_filter_sort():
    app = create_app()
    client = TestClient(app)

    client.post("/items/", json={"name": "x", "value": 1})
    client.post("/items/", json={"name": "y", "value": 3})
    client.post("/items/", json={"name": "z", "value": 2})

    r = client.get("/items/", params={"sort_by": "value", "sort_dir": "desc"})
    assert r.status_code == 200
    data = r.json()
    vals = [i["value"] for i in data]
    assert vals == sorted(vals, reverse=True)

    r = client.get("/items/", params={"limit": 2})
    assert r.status_code == 200
    assert len(r.json()) <= 2
    
    r = client.get("/items/", params=[("filters", "name:x")])
    assert r.status_code == 200
    data = r.json()
    assert all(d["name"] == "x" for d in data)


def test_operation_dependencies():
    def deny():
        raise HTTPException(status_code=401, detail="unauthorized")

    app = create_app(operation_deps={"create": [deny]})
    client = TestClient(app)

    r = client.post("/items/", json={"name": "no", "value": 0})
    assert r.status_code == 401
