from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from app.models import Base


from typing import Generator, Optional
from sqlalchemy.orm import Session, sessionmaker


def get_db(
    session_maker: Optional[sessionmaker] = None,
) -> Generator[Session, None, None]:
    """
    Returns a DB session from the given sessionmaker, or the default if not provided.
    """
    from sqlalchemy.orm import sessionmaker as _sessionmaker
    from sqlalchemy import create_engine
    from pathlib import Path
    from app.models import Base

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
