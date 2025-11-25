from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = f"""
postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:
{os.getenv('POSTGRES_PASSWORD')}@
{os.getenv('POSTGRES_HOST')}:
{os.getenv('POSTGRES_PORT')}/
{os.getenv('POSTGRES_DB')}
""".replace("\n", "").strip()   #need to remove the line breaks OR strip them — otherwise SQLAlchemy may get whitespace in the URL

engine=create_engine(DATABASE_URL)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base=declarative_base()