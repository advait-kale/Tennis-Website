from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL_DATABASE = 'postgresql://postgres:1234!localhost::5432/matches'

engine = create_engine(
    url=URL_DATABASE
)

sessionLocal = sessionmaker(
    autocommit = False,
    autoflush= False,
    bind = engine
)


base = declarative_base()
