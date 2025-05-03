"""
Default data operations
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Base

ModelType = TypeVar("ModelType", bound=Base)  # pylint: disable=invalid-name
CreateSchemaType = TypeVar(
    "CreateSchemaType", bound=BaseModel
)  # pylint: disable=invalid-name
UpdateSchemaType = TypeVar(
    "UpdateSchemaType", bound=BaseModel
)  # pylint: disable=invalid-name


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    CRUD object with default methods
    """

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get_by_id(self, db: Session, obj_id: Any) -> Optional[ModelType]:
        """
        Get object by id
        None if nothing found
        """
        res = db.scalar(select(self.model).filter(self.model.id == obj_id).limit(1))
        return res

    def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get objects (paginated)
        """
        res = db.scalars(
            select(self.model).order_by(self.model.id).offset(skip).limit(limit)
        )
        return res.all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """
        Store new object in database
        """
        db_obj = self.model(**obj_in.model_dump())  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """
        Update some object fields with new data
        """
        obj_data = db_obj
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data.__dict__:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_by_id(self, db: Session, obj_id: int) -> ModelType:
        """
        Delete object from database by id
        """
        obj = self.get_by_id(db, obj_id)
        db.delete(obj)
        db.commit()
        return obj
