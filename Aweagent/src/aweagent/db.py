import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# Database setup
Base = declarative_base()


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(String(50))
    title = Column(String(1000))
    authors = Column(Text)
    year = Column(Integer)
    url = Column(String(500))
    publication_types = Column(String(500))
    venue = Column(String(500))
    journal = Column(String(500))
    doi = Column(String(50))
    search_date = Column(Date, default=datetime.datetime.now)
    search_query = Column(String(500))
    abstract = Column(Text)
    citationCount = Column(Integer)
    citationStyles = Column(Text)
    citations = Column(Text)
    corpusId = Column(String(50))
    embedding = Column(Text)
    externalIds = Column(Text)
    fieldsOfStudy = Column(Text)
    influentialCitationCount = Column(Integer)
    isOpenAccess = Column(Boolean)
    journal = Column(String(500))
    keys = Column(Text)
    openAccessPdf = Column(String(500))
    paperId = Column(String(50))
    publicationDate = Column(Date)
    publicationTypes = Column(Text)
    publicationVenue = Column(String(500))
    raw_data = Column(Text)
    referenceCount = Column(Integer)
    domain = Column(String(500))
    category = Column(String(500))


def get_database_session(db_path: str = None):
    """Get a database session"""
    if db_path and not os.path.exists(db_path):
        os.makedirs(db_path)

    database_url = f"sqlite:///{os.path.join(db_path, 'SemanticScholar_papers.db')}" if db_path else os.getenv("DATABASE_URL", "sqlite:///SemanticScholar_papers.db")
    
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
