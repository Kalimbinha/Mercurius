from typing import Type, List, Optional, Sequence, Callable
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel


def Mercurius(
    app,
    model: Type,
    read_schema: Type[BaseModel],
    db_session: Callable[[], Session],
    *,
    create_schema: Optional[Type[BaseModel]] = None,
    update_schema: Optional[Type[BaseModel]] = None,
    prefix: Optional[str] = None,
    pk_name: str = "id",
    operations: Sequence[str] = ("list", "get", "create", "update", "delete"),
    tags: Optional[List[str]] = None,
    operation_dependencies: Optional[dict] = None,
    filter_fields: Optional[Sequence[str]] = None,
    sort_fields: Optional[Sequence[str]] = None,
):
    """
    Cria automaticamente rotas CRUD para o modelo SQLAlchemy informado.
    """

    if db_session is None:
        raise ValueError("db_session dependency is required")

    router = APIRouter()
    prefix = prefix or getattr(model, "__tablename__", model.__name__.lower())
    tags = tags or [prefix]

    pk_attr = getattr(model, pk_name)

    operation_dependencies = operation_dependencies or {}

    def _deps_for(op: str):
        deps = []
        if operation_dependencies and isinstance(operation_dependencies, dict):
            for d in operation_dependencies.get(op, []):
                deps.append(Depends(d))
        return deps

    def _payload_to_dict(payload, exclude_unset: bool = False):
        if hasattr(payload, "model_dump"):
            return payload.model_dump(exclude_unset=exclude_unset)
        return payload.dict(exclude_unset=exclude_unset)

    if "list" in operations:
        deps = _deps_for("list")

        @router.get("/", response_model=List[read_schema], tags=tags, dependencies=deps)
        def list_items(
            skip: int = 0,
            limit: int = 100,
            sort_by: Optional[str] = None,
            sort_dir: str = "asc",
            filters: Optional[List[str]] = Query(None, description="filters as field:value"),
            db: Session = Depends(db_session),
        ):
            q = db.query(model)

            for f in filters or []:
                if ":" not in f:
                    continue
                field, val = f.split(":", 1)
                if filter_fields is not None and field not in filter_fields:
                    continue
                if hasattr(model, field):
                    col = getattr(model, field)
                    if isinstance(val, str) and val.isdigit():
                        val_cast = int(val)
                    else:
                        try:
                            val_cast = float(val)
                        except Exception:
                            val_cast = val
                    q = q.filter(col == val_cast)

            if sort_by and (sort_fields is None or sort_by in sort_fields) and hasattr(model, sort_by):
                col = getattr(model, sort_by)
                if str(sort_dir).lower() == "desc":
                    q = q.order_by(col.desc())
                else:
                    q = q.order_by(col.asc())

            q = q.offset(skip).limit(limit)
            return q.all()

    if "get" in operations:
        deps = _deps_for("get")
        @router.get("/{item_id}", response_model=read_schema, tags=tags, dependencies=deps)
        def get_item(item_id: int, db: Session = Depends(db_session)):
            item = db.query(model).filter(pk_attr == item_id).first()
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return item

    if "create" in operations:
        in_schema = create_schema or read_schema
        deps = _deps_for("create")

        @router.post("/", response_model=read_schema, status_code=status.HTTP_201_CREATED, tags=tags, dependencies=deps)
        def create_item(payload, db: Session = Depends(db_session)):
            obj = model(**_payload_to_dict(payload))
            try:
                db.add(obj)
                db.commit()
                db.refresh(obj)
                return obj
            except Exception as exc:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(exc))

        try:
            create_item.__annotations__["payload"] = in_schema
            create_item.__annotations__["db"] = Session
            create_item.__annotations__["return"] = read_schema
        except Exception:
            pass

    if "update" in operations:
        in_update = update_schema or read_schema
        deps = _deps_for("update")

        @router.put("/{item_id}", response_model=read_schema, tags=tags, dependencies=deps)
        def update_item(item_id: int, payload, db: Session = Depends(db_session)):
            existing = db.query(model).filter(pk_attr == item_id).first()
            if not existing:
                raise HTTPException(status_code=404, detail="Item not found")

            data = _payload_to_dict(payload, exclude_unset=True)
            for key, value in data.items():
                setattr(existing, key, value)

            try:
                db.commit()
                db.refresh(existing)
                return existing
            except Exception as exc:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(exc))

        try:
            update_item.__annotations__["payload"] = in_update
            update_item.__annotations__["db"] = Session
            update_item.__annotations__["return"] = read_schema
        except Exception:
            pass

    if "delete" in operations:
        deps = _deps_for("delete")

        @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=tags, dependencies=deps)
        def delete_item(item_id: int, db: Session = Depends(db_session)):
            existing = db.query(model).filter(pk_attr == item_id).first()
            if not existing:
                raise HTTPException(status_code=404, detail="Item not found")
            try:
                db.delete(existing)
                db.commit()
                return None
            except Exception as exc:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(exc))

    app.include_router(router, prefix=f"/{prefix}")


__all__ = ["Mercurius"]
