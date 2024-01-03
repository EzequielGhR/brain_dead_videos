from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional

class Base(DeclarativeBase): pass

class PostTable(Base):
    __tablename__ = "post_data"

    id:Mapped[str] = mapped_column(String(30), primary_key=True)
    author:Mapped[str] = mapped_column(String(30))
    post_text:Mapped[str] = mapped_column(Text())
    post_url:Mapped[str] = mapped_column(String(300))
    readable_stamp:Mapped[str] = mapped_column(String(100))
    readable_subreddit:Mapped[str] = mapped_column(String(30))
    subreddit:Mapped[str] = mapped_column(String(30))
    timestamp:Mapped[datetime] = mapped_column(DateTime(timezone=True))
    title:Mapped[str] = mapped_column(String(300))
    created_at = mapped_column(DateTime(timezone=True), default=func.now())

    multimedia = relationship("MultiMediaTable", back_populates="post_data", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Post(id={self.id!r}, title={self.title!r}, url={self.post_url!r})"

class MultiMediaTable(Base):
    __tablename__ = "multimedia"

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    audio_uri:Mapped[str] = mapped_column(String(300))
    video_uri:Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    subs_uri:Mapped[str] = mapped_column(String(300))
    post_id = mapped_column(ForeignKey("post_data.id"), unique=True)
    created_at = mapped_column(DateTime(timezone=True), default=func.now())

    post_data = relationship("PostTable", back_populates="multimedia", uselist=False, single_parent=True)

    def __repr__(self) -> str:
        return f"MultiMedia(id={self.id!r}, post_id={self.post_id!r})"