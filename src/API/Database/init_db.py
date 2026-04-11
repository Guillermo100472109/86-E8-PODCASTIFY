from sqlalchemy import create_all, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ruta de la BD coincidiendo con la carpeta del Docker
DATABASE_URL = "sqlite:////app/data/noticias.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    import src.API.models as models # Importa tus modelos (User, Keyword, etc.)
    Base.metadata.create_all(bind=engine)