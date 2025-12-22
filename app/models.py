from datetime import datetime
from typing import Annotated, List, Optional

from sqlalchemy import Column, ForeignKey, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

intpk = Annotated[int, mapped_column(primary_key=True, index=True)]
str_256 = Annotated[str, mapped_column(String(256), index=True)]

tweet_likes = Table(
    "tweet_likes",
    Base.metadata,
    Column(
        "tweet_id",
        ForeignKey("tweets.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "user_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

user_follows = Table(
    "user_follows",
    Base.metadata,
    Column(
        "follower_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "followed_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    name: Mapped[str_256]
    api_key: Mapped[str] = mapped_column(String(256), unique=True, index=True)

    tweets: Mapped[List["Tweet"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    liked_tweets: Mapped[List["Tweet"]] = relationship(
        secondary=tweet_likes, back_populates="likes"
    )
    followers: Mapped[List["User"]] = relationship(
        secondary=user_follows,
        primaryjoin="User.id == user_follows.c.followed_id",
        secondaryjoin="User.id == user_follows.c.follower_id",
        back_populates="following",
    )
    following: Mapped[List["User"]] = relationship(
        secondary=user_follows,
        primaryjoin="User.id == user_follows.c.follower_id",
        secondaryjoin="User.id == user_follows.c.followed_id",
        back_populates="followers",
    )
    repr_cols_num = 2


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[intpk]
    content: Mapped[str] = mapped_column(String(1024))
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), index=True
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    author: Mapped["User"] = relationship(back_populates="tweets")
    likes: Mapped[List[User]] = relationship(
        secondary=tweet_likes, back_populates="liked_tweets"
    )
    medias: Mapped[List["Media"]] = relationship(
        back_populates="tweet", cascade="all, delete-orphan"
    )


class Media(Base):
    __tablename__ = "medias"

    id: Mapped[intpk]
    file_path: Mapped[str] = mapped_column(String(256))

    tweet_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tweets.id", ondelete="CASCADE"), index=True
    )
    tweet: Mapped[Optional["Tweet"]] = relationship(back_populates="medias")
