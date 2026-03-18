from datetime import date
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.db.session import get_engine

router = APIRouter(prefix="/humans", tags=["Humans"])


class HumanCreate(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=50)
    dob: date | None = None
    gender: Literal["M", "F"] | None = None
    typeid: int = Field(gt=0)


class HumanRead(BaseModel):
    id: int
    name: str
    dob: date | None
    gender: str | None
    typeid: int
    type_name: str


class HumanTypeRead(BaseModel):
    typeid: int
    name: str


class HumanTypeCreate(BaseModel):
    typeid: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=50)


@router.get("", response_model=list[HumanRead])
def list_humans() -> list[HumanRead]:
    query = text(
        """
        SELECT
            h.id,
            h.name,
            h.dob,
            h.gender,
            h.typeid,
            ht.name AS type_name
        FROM Human h
        INNER JOIN HumanType ht ON h.typeid = ht.typeid
        ORDER BY h.id ASC
        """
    )

    engine = get_engine()
    with engine.connect() as connection:
        rows = connection.execute(query).mappings().all()

    return [HumanRead.model_validate(dict(row)) for row in rows]


@router.get("/types", response_model=list[HumanTypeRead])
def list_human_types() -> list[HumanTypeRead]:
    query = text(
        """
        SELECT typeid, name
        FROM HumanType
        ORDER BY typeid ASC
        """
    )

    engine = get_engine()
    with engine.connect() as connection:
        rows = connection.execute(query).mappings().all()

    return [HumanTypeRead.model_validate(dict(row)) for row in rows]


@router.post("/types", status_code=201)
def create_human_type(payload: HumanTypeCreate) -> dict[str, str]:
    insert_query = text(
        """
        INSERT INTO HumanType (typeid, name)
        VALUES (:typeid, :name)
        """
    )

    engine = get_engine()

    try:
        with engine.begin() as connection:
            connection.execute(insert_query, payload.model_dump())
    except IntegrityError as exc:
        message = str(exc.orig) if exc.orig else str(exc)
        raise HTTPException(status_code=400, detail=f"Cannot insert human type: {message}") from exc

    return {"message": "Human type created successfully"}


@router.post("", status_code=201)
def create_human(payload: HumanCreate) -> dict[str, str]:
    check_type_query = text("SELECT 1 FROM HumanType WHERE typeid = :typeid")
    insert_query = text(
        """
        INSERT INTO Human (id, name, dob, gender, typeid)
        VALUES (:id, :name, :dob, :gender, :typeid)
        """
    )

    engine = get_engine()

    try:
        with engine.begin() as connection:
            type_exists = connection.execute(check_type_query, {"typeid": payload.typeid}).scalar()
            if not type_exists:
                raise HTTPException(status_code=400, detail="typeid does not exist in HumanType")

            connection.execute(insert_query, payload.model_dump())
    except IntegrityError as exc:
        message = str(exc.orig) if exc.orig else str(exc)
        raise HTTPException(status_code=400, detail=f"Cannot insert human: {message}") from exc

    return {"message": "Human created successfully"}
