"""Create SQLAlchemy engine and session objects."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import ProdConfig

# Create database engine
engine = create_engine(ProdConfig.DATABASE_URL)

# Create database session
Session = sessionmaker(bind=engine)
session = Session()
