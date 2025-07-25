from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL="postgresql://postgres:password@localhost:5432/Quiz-application"

engine=create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base=declarative_base()

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL="postgresql://postgres:password@localhost:5432/todos"

# engine=create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base=declarative_base()