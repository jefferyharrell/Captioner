from sqlalchemy import Column, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Photo(Base):
    __tablename__: str = "photos"
    hash = Column(String(255), primary_key=True)
    filename = Column(String(255))
    caption = Column(Text, nullable=True)
    # Add future metadata fields here as needed

    @property
    def hash_value(self) -> str:
        return self.__dict__["hash"]

    @property
    def filename_value(self) -> str:
        return self.__dict__["filename"]

    @property
    def caption_value(self) -> str | None:
        return self.__dict__["caption"]
