import logging
from urllib.parse import quote

import bcrypt
from sqlalchemy import Column, String
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

import hodor
from hodor import AppContext

LOGGER = logging.getLogger('lorem-ipsum')

Base = declarative_base()


class Transaction:
    _db = None
    _session_maker = None
    _connection_pool_stats = {'usedconn': 0}

    def __init__(self, app_context: hodor.AppContext):
        self._session = None
        self.config = app_context.config

    @staticmethod
    def db() -> Engine:
        return Transaction._db

    @staticmethod
    def pool() -> QueuePool:
        return Transaction._db.pool

    def __new_session(self):
        return Transaction._session_maker()

    @property
    def session(self) -> Session:
        return self._session

    def __enter__(self):
        self._session = self.__new_session()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            LOGGER.debug(f'Commit connection for session transaction {self.session.transaction}')
            self.session.commit()
        except:
            print('Database error...')
            self.session.rollback()
            raise
        finally:
            LOGGER.debug(f'Closing connection for session {self.session.transaction}')
            self.session.close()


class TransactionManager:
    def __init__(self, app_context: AppContext):
        self.config = app_context.config

        if Transaction._db is None:
            user = self.config['aurora_user']
            password = quote(self.config['aurora_password'])
            host = self.config['aurora_host']
            port = self.config['aurora_port']
            database = self.config['database_name']
            minconn = self.config.get('connection_pool_minconn')
            maxconn = self.config.get('connection_pool_maxconn')
            self.database_connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            _db = create_engine(self.database_connection_string,
                                pool_size=minconn, max_overflow=maxconn - minconn, poolclass=QueuePool, echo=False)
            Transaction._db = _db
            Transaction._session_maker = sessionmaker(_db)
            LOGGER.debug(f'Created db {Transaction._db}')
        self._transaction = Transaction(app_context)

    @property
    def transaction(self) -> Transaction:
        return self._transaction


def transaction(function):
    def wrapper(self, *args, **kwargs):
        _result = None
        with self._app_context.transaction_manager.transaction as _tm:
            _result = function(self, *args, **kwargs)
        return _result

    return wrapper


class User(Base):
    __tablename__ = 'users1'

    username = Column(String, primary_key=True)
    password = Column(String)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c != User.password}

    @staticmethod
    def from_dict(data: dict):
        return User(**data)


class UserRepo:
    def __init__(self, app_context: hodor.AppContext):
        self._transaction_manager = app_context.transaction_manager

    def is_password_valid(self, user: User):
        _session = self._transaction_manager.transaction.session
        result = _session.query(User).filter(
            User.username == user.username and User.password == user.password).first()
        if result is None:
            return False
        return True

    def get(self, username=None) -> User:
        _session = self._transaction_manager.transaction.session
        user = _session.query(User).filter(User.username == username).first()
        return user

    def delete(self, user):
        _session = self._transaction_manager.transaction.session
        _session.delete(user)

    def get_all(self, limit=10):
        _session = self._transaction_manager.transaction.session
        count = _session.query(User).count()
        users = _session.query(User).limit(limit)
        return {"total": count, "items": users}

    def save(self, user: User):
        LOGGER.info(f'data = {user.as_dict()}')
        _session = self._transaction_manager.transaction.session
        _session.add(user)
        return user

    def encrypt_password(self, pwd):
        encrypted_password = bcrypt.hashpw(password=pwd.encode('utf-8'),
                                           salt=self._transaction_manager.config['password_encryption_key'].encode(
                                               'utf-8'))
        return encrypted_password


def db_setup(app_context: AppContext):
    LOGGER.debug('Creating table...')
    _db_name = app_context.config.get('db_name', 'lorem-ipsum')
    _cursor = app_context.transaction_manager.transaction.session
    # _cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{_db_name}'")
    # exists = _cursor.fetchone()
    # if not exists:
    #     _cursor.execute(f'CREATE DATABASE {_db_name}')
    _cursor.execute('CREATE TABLE IF NOT EXISTS public.users1\
        (\
            username character varying(50) COLLATE pg_catalog."default" NOT NULL,\
            password character varying(200) COLLATE pg_catalog."default" NOT NULL,\
            CONSTRAINT user_pk PRIMARY KEY (username)\
        )')
    if app_context.user_repo.get(app_context.config['admin_user']) is None:
        password_plain = app_context.config['admin_password']
        password_encrypted = app_context.user_repo.encrypt_password(password_plain)
        app_context.user_repo.save(User.from_dict(
            {'username': app_context.config['admin_user'], 'password': password_encrypted}))
