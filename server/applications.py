from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from deps import get_db, get_current_user
from models import Application, User
from schemas import ApplicationCreate, ApplicationUpdate, ApplicationOut, Status

router = APIRouter(prefix="/applications", tags=["applications"])

DB = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_owned_application(app_id: int, db: Session, user: User) -> Application:
    application = db.get(Application, app_id)
    if application is None or application.user_id != user.id:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.get("", response_model=list[ApplicationOut])
def list_applications(db: DB, user: CurrentUser, status: Status | None = None, q: str | None = None):
    stmt = select(Application).where(Application.user_id == user.id)
    if status:
        stmt = stmt.where(Application.status == status)
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(or_(Application.company.ilike(pattern), Application.role.ilike(pattern)))
    stmt = stmt.order_by(Application.created_at.desc())
    return db.scalars(stmt).all()


@router.post("", response_model=ApplicationOut, status_code=201)
def create_application(data: ApplicationCreate, db: DB, user: CurrentUser):
    application = Application(**data.model_dump(), user_id=user.id)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/{app_id}", response_model=ApplicationOut)
def get_application(app_id: int, db: DB, user: CurrentUser):
    return get_owned_application(app_id, db, user)


@router.patch("/{app_id}", response_model=ApplicationOut)
def update_application(app_id: int, data: ApplicationUpdate, db: DB, user: CurrentUser):
    application = get_owned_application(app_id, db, user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    db.commit()
    db.refresh(application)
    return application


@router.delete("/{app_id}", status_code=204)
def delete_application(app_id: int, db: DB, user: CurrentUser):
    application = get_owned_application(app_id, db, user)
    db.delete(application)
    db.commit()