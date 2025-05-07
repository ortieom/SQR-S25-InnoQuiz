from sqlalchemy import create_engine
from backend.config import settings
from backend.models.user import Base as UserBase
from backend.models.quiz import Base as QuizBase

def init_db():
    # Create engine
    engine = create_engine(str(settings.DATABASE_URL))
    
    # Create all tables
    UserBase.metadata.create_all(bind=engine)
    QuizBase.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 