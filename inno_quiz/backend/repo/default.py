"""
Default data operations
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend import models
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

    async def get_by_id(self, db: AsyncSession, obj_id: Any) -> Optional[ModelType]:
        """
        Get object by id
        None if nothing found
        """
        res = await db.scalar(
            select(self.model).filter(self.model.id == obj_id).limit(1)
        )
        return res

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get objects (paginated)
        """
        res = await db.scalars(
            select(self.model).order_by(self.model.id).offset(skip).limit(limit)
        )
        return res.all()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """
        Store new object in database
        """
        db_obj = self.model(**obj_in.model_dump())  # type: ignore

        # custom string id
        if self.model.id.type.python_type is str and db_obj.id is None:
            # format class_name-number
            model_id = f"{self.model.__name__.lower()}-{await self.get_new_id_cnt(db)}"
            setattr(db_obj, "id", model_id)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
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
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove_by_id(self, db: AsyncSession, obj_id: int) -> ModelType:
        """
        Delete object from database by id
        """
        obj = await self.get_by_id(db, obj_id)
        await db.delete(obj)
        await db.commit()
        return obj
