from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Column, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from quart_project.db_interface import Base

# abstract parent class to provide default fields + helper functions to all DB models which inherit this
class BaseModel(Base):
    __abstract__ = True 

    # all classes have an ID primary key which is auto incremented, and a time_updated field which will auto update when row is updated
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    time_updated = Column(DateTime(timezone=True))

    # session needed for all below functions: session is similar to a connection
    # connection does the work of executing SQL Query with some added control features such as commit/rollback: raw SQL
    # session is the ORM portion of SQLAlchemy background uses connections with auto generated SQL statements

    # class method: returns an array of Instances of the class from the database
    @classmethod
    async def get_all(cls, session: AsyncSession):
        result = await session.execute(select(cls))
        # scalars returns the first col of each row from .execute(); therefore returns an array of all instances of the class
        return result.scalars().all()

    # session.get() will return the class with the primary key id passed to this argument
    @classmethod
    async def get_by_id(cls, session: AsyncSession, obj_id: int):
        return await session.get(cls, obj_id)

    # add the passed in object to the table it belongs to and returns the added user
    @classmethod
    async def add(cls, session: AsyncSession, obj):
        session.add(obj)
        obj.time_updated = datetime.now()
        # commit() will commit the session in progress; obj is still attached to the session and will be until the session is closed
        await session.commit()
        await session.refresh(obj)
        return obj

    # obj acts as a proxy for row in DB; if obj.<field_name> is edited Session tracks the change and now the obj will be in: session.dirty
    # thus get your object you want to edit. obj.field_name = new_val. Then on next session flush (commit) the DB will be updated with all changes
    @classmethod
    async def edit(cls, session: AsyncSession, obj):
        obj.time_updated = datetime.now()
        await session.commit()
        await session.refresh(obj)
        return obj

    # session.delete(obj) will mark the object for deletion; session.commit() will force delete it from the database
    @classmethod
    async def delete(cls, session: AsyncSession, obj):
        await session.delete(obj)
        await session.commit()

    # converts the class to a dictionary so it can be easily returned by Quart
    def to_dict(self):
        result = {}
        for key, value in vars(self).items():
            # skip private attributes
            if key.startswith("_"):
                continue
            # convert datetime attributes to iso so they are json serializable
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            # otherwise just simply append
            else:
                result[key] = value
        return result

    # dev notes
    # python **kwargs is just stringing out the remaining keyword args passed in --> then making a class with them (not good) - want to pass in an obj
    # session.flush() is called to emit the current SQL to the database
    # session.flush() is usually unnecessary due to autoflushing which will happen when session.commit() is called
    # autoflushing will also occur from within a session if ANY other query is emitted --> if you delete but dont flush; flush will auto happen before next UPDATE/ADD/SELECT