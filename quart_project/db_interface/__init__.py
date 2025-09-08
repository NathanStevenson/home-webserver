from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from quart_project.secrets.secrets import DATABASE_URL

# Declarative Base provides a simple way to define DB Tables as classes in Python
Base = declarative_base()

# Class containing utility functions for interacting with the database
class DatabaseInterface:
    def __init__(self, db_url):
        # creates an async SQL alchemy engine (connection pool ) corresponding with the provided DB URL
        self.engine = create_async_engine(db_url, echo=True)
        # Factory for database sessions; session uses the Engine to interact with the database from within the Session
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    # when initializing the db create all the tables which inherit from declarative_base; if the db already exists use that and do not recreate it
    async def init_db(self):
        async with self.engine.begin() as connection:
            # create new DB tables - eventually get alembic working for DB migrations
            await connection.run_sync(Base.metadata.create_all)

    # close out the engine, close down all connections, called when shutting down the server
    async def close_db(self):
        await self.engine.dispose()

    # call when want to delete all the DB's data and restart (eventually will want migrations)
    async def clear_db(self):
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)

    # create a new session to write/read values from the database
    def create_session(self):
        return self.session_factory()
    
# set up an easy to use interface with the database URL provided
db_interface = DatabaseInterface(DATABASE_URL)