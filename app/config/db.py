import os

from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


class SqlAlchemyConfig:  # pragma: no cover
    @staticmethod
    def create_engine(
        database: str = None,
        dialect: str = None,
        driver: str = None,
        host: str = None,
        password: str = None,
        port: int = None,
        query_args: str = None,
        user: str = None,
        **kwargs,
    ) -> Engine:
        database = database or os.environ["SqlAlchemyDatabase"]
        dialect = dialect or os.environ["SqlAlchemyDialect"]
        driver = driver or os.environ["SqlAlchemyDriver"]
        host = host or os.environ["SqlAlchemyHost"]
        password = password or os.environ["SqlAlchemyPassword"]
        port = port or int(os.environ.get("SqlAlchemyPort", 3306))
        query_args = query_args or os.environ.get("SqlAlchemyQueryArgs")
        user = user or os.environ["SqlAlchemyUser"]
        # Assemble drivername according to SQLAlchemy scheme: "dialect+driver"
        # If driver is not provided, use only the dialect part
        drivername = f"{dialect}+{driver}" if driver else dialect
        url = URL.create(
            drivername=drivername,
            username=user,
            password=password,
            host=host,
            port=port,
            database=database,
            query=query_args,
        )
        return create_engine(url, **kwargs)

    @classmethod
    def create_session_maker(cls, **kwargs) -> sessionmaker:
        return sessionmaker(cls.engine(), **kwargs)

    @classmethod
    def engine(cls, **kwargs) -> Engine:
        return cls.create_engine(**kwargs)

    @classmethod
    def session(cls, **kwargs) -> Session:
        return cls.create_session_maker(**kwargs)()
