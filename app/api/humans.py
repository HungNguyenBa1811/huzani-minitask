import re
from datetime import date
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.db.session import get_engine

router = APIRouter(prefix="/humans", tags=["Humans"])

# Whitelist: unicode word chars (letters/digits/_), spaces, hyphens, dots only.
# Apostrophes and other SQL-sensitive chars are intentionally excluded (defense-in-depth).
# Parameterized queries already prevent SQL injection at the DB layer.
_NAME_PATTERN = re.compile(r"^[\w\s\-\.]+$", re.UNICODE)
_SQL_SPECIAL_CHARS = re.compile(r"[;'\"`\\=<>()|&%+*!]")
_DOB_MIN_YEAR = 1900


def _validate_name(v: str) -> str:
    v = v.strip()
    if not v:
        raise ValueError("must not be blank or whitespace only")
    if _SQL_SPECIAL_CHARS.search(v):
        raise ValueError("must not contain special characters (;, ', \", `, \\, =, <, >, (, ), |, &, %, +, *, !)")
    if not _NAME_PATTERN.match(v):
        raise ValueError("must contain only letters, digits, spaces, hyphens, or dots")
    return v


class HumanCreate(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=50)
    dob: date | None = None
    gender: Literal["M", "F"] | None = None
    typeid: int = Field(gt=0)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return _validate_name(v)

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, v: date | None) -> date | None:
        if v is None:
            return v
        if v > date.today():
            raise ValueError("date of birth must not be in the future")
        if v.year < _DOB_MIN_YEAR:
            raise ValueError(f"date of birth must be on or after {_DOB_MIN_YEAR}-01-01")
        return v


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

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return _validate_name(v)


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
