from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models import Media, Tweet, User, tweet_likes


async def get_user_by_api_key(db: AsyncSession, api_key: str):
    query_result = await db.execute(
        select(User)
        .options(joinedload(User.following))
        .filter(User.api_key == api_key)
    )
    return query_result.scalars().unique().one_or_none()


async def create_tweet(
    db: AsyncSession,
    user_id: int,
    content: str,
    media_ids: Optional[List[int]] = None,
) -> Tweet:
    tweet = Tweet(content=content, author_id=user_id)
    db.add(tweet)
    await db.commit()

    tweet_query = await db.execute(
        select(Tweet)
        .options(selectinload(Tweet.medias))
        .filter(Tweet.id == tweet.id)
    )
    tweet = tweet_query.scalar_one()

    if media_ids:
        medias_query = await db.execute(
            select(Media).filter(Media.id.in_(media_ids))
        )
        medias = medias_query.scalars().all()
        for media in medias:
            media.tweet_id = tweet.id
        tweet.medias.extend(medias)
        await db.commit()
    return tweet


async def delete_tweet(db: AsyncSession, tweet_id: int, user_id: int) -> bool:
    result = await db.execute(
        select(Tweet).filter(Tweet.id == tweet_id, Tweet.author_id == user_id)
    )
    tweet = result.scalar_one_or_none()
    if not tweet:
        return False
    await db.delete(tweet)
    await db.commit()
    return True


async def like_tweet(db: AsyncSession, tweet_id: int, user: User):
    result = await db.execute(
        select(Tweet)
        .options(selectinload(Tweet.likes))
        .filter(Tweet.id == tweet_id)
    )
    tweet = result.scalar_one_or_none()
    if tweet is None:
        raise HTTPException(status_code=404, detail="Твит не найден")
    if user not in tweet.likes:
        tweet.likes.append(user)
        await db.commit()


async def unlike_tweet(db: AsyncSession, tweet_id: int, user: User):
    result = await db.execute(
        select(Tweet)
        .options(selectinload(Tweet.likes))
        .filter(Tweet.id == tweet_id)
    )
    tweet = result.scalar_one_or_none()
    if tweet is None:
        raise HTTPException(status_code=404, detail="Твит не найден")
    if user in tweet.likes:
        tweet.likes.remove(user)
        await db.commit()


async def follow_user(db: AsyncSession, target_id: int, user: User):
    result = await db.execute(
        select(User)
        .options(selectinload(User.followers))
        .filter(User.id == target_id)
    )
    target = result.scalar_one_or_none()
    if not target or target == user:
        raise HTTPException(status_code=400, detail="Invalid target")
    if user not in target.followers:
        target.followers.append(user)
        await db.commit()


async def unfollow_user(db: AsyncSession, target_id: int, user: User):
    result = await db.execute(
        select(User)
        .options(selectinload(User.followers))
        .filter(User.id == target_id)
    )
    target = result.scalar_one_or_none()
    if target and user in target.followers:
        target.followers.remove(user)
        await db.commit()


async def get_feed(db: AsyncSession, user: User) -> List[Tweet]:
    if not user.following:
        return []
    subq = (
        select(Tweet.id, func.count(tweet_likes.c.user_id).label("like_count"))
        .filter(
            Tweet.author_id.in_([user.id] + [f.id for f in user.following])
        )
        .outerjoin(tweet_likes, tweet_likes.c.tweet_id == Tweet.id)
        .group_by(Tweet.id)
        .subquery()
    )
    query = (
        select(Tweet)
        .join(subq, Tweet.id == subq.c.id)
        .order_by(desc(subq.c.like_count), desc(Tweet.created_at))
    )
    result = await db.execute(
        query.options(
            selectinload(Tweet.likes),
            selectinload(Tweet.medias),
            joinedload(Tweet.author),
        )
    )
    return list(result.scalars().unique().all())


async def get_user_profile(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(
        select(User)
        .options(joinedload(User.followers), joinedload(User.following))
        .filter(User.id == user_id)
    )
    user = result.unique().scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


async def create_media(db: AsyncSession, file_path: str) -> Media:
    media = Media(file_path=file_path)
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media
