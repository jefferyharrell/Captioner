from app.models import Photo
from sqlalchemy.orm import Session
from typing import Optional, List

def add_photo(db: Session, hash: str, filename: str, caption: Optional[str] = None) -> Photo:
    photo = Photo(hash=hash, filename=filename, caption=caption)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo

def get_photo_by_hash_filename(db: Session, hash: str, filename: str) -> Optional[Photo]:
    return db.query(Photo).filter_by(hash=hash, filename=filename).first()

def get_all_photos(db: Session) -> List[Photo]:
    return db.query(Photo).all()

def update_photo_caption(db: Session, hash: str, filename: str, caption: str) -> Optional[Photo]:
    photo = db.query(Photo).filter_by(hash=hash, filename=filename).first()
    if not photo:
        return None
    photo.caption = caption
    db.commit()
    db.refresh(photo)
    return photo
