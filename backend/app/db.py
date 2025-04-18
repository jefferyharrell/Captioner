from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Optional
from app.models import Base


def get_db(
    session_maker: Optional[sessionmaker[Session]] = None,
) -> Generator[Session, None, None]:
    """
    Returns a DB session from the given sessionmaker, or the default if not provided.
    """
    from sqlalchemy.orm import sessionmaker as _sessionmaker
    from sqlalchemy import create_engine
    from pathlib import Path

    if session_maker is None:
        db_path = Path(__file__).parent.parent / "photos.db"
        engine = create_engine(
            f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
        )
        session_maker = _sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
    db = session_maker()
    try:
        yield db
    finally:
        db.close()
