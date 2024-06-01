from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from conn import *


DSN = f'postgresql://{USER}:{PASSWORD}@localhost:5432/{DATABASE}'


def session_decorator(func):
    def wrapper(self, *args, **kwargs):
        engine = create_engine(DSN)
        Session = sessionmaker(bind=engine)
        with Session() as session:
            return func(self, session, *args, **kwargs)
    return wrapper


def engine_decorator(func):
    def wrapper(*args, **kwargs):
        engine = create_engine(DSN)
        return func(engine, *args, **kwargs)
    return wrapper