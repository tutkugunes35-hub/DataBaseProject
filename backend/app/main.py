from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .db import engine, SessionLocal, Base
from .models import Item

class HealthResponse(BaseModel):
    status: str
    db: bool | None = None

class ItemCreate(BaseModel):
    name: str

class ItemOut(BaseModel):
    id: int
    name: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Backend", version="0.1.0", lifespan=lifespan)

@app.get("/", tags=["root"])
def root():
    return {"message": "Backend is running", "docs": "/docs", "openapi": "/openapi.json", "health": "/health"}

@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health():
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))
        return {"status": "ok", "db": True}
    except Exception:
        return {"status": "ok", "db": False}

@app.post("/items", response_model=ItemOut, tags=["items"])
async def create_item(payload: ItemCreate):
    try:
        async with SessionLocal() as session:
            item = Item(name=payload.name)
            session.add(item)
            await session.commit()
            await session.refresh(item)
            return {"id": item.id, "name": item.name}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="DB error")

@app.get("/items", response_model=list[ItemOut], tags=["items"])
async def list_items():
    async with SessionLocal() as session:
        res = await session.execute(select(Item).order_by(Item.id))
        items = res.scalars().all()
        return [{"id": i.id, "name": i.name} for i in items]

@app.get("/items/{item_id}", response_model=ItemOut, tags=["items"])
async def get_item(item_id: int):
    async with SessionLocal() as session:
        res = await session.execute(select(Item).where(Item.id == item_id))
        item = res.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="Not found")
        return {"id": item.id, "name": item.name}

@app.delete("/items/{item_id}", tags=["items"])
async def delete_item(item_id: int):
    async with SessionLocal() as session:
        res = await session.execute(select(Item).where(Item.id == item_id))
        item = res.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="Not found")
        await session.delete(item)
        await session.commit()
        return {"deleted": True, "id": item_id}
