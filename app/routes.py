import os
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.crud import (
    create_media,
    create_tweet,
    delete_tweet,
    follow_user,
    get_feed,
    get_user_profile,
    like_tweet,
    unfollow_user,
    unlike_tweet,
)
from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas import (
    OperationResponse,
    TweetCreate,
    TweetsResponse,
    UserResponse,
)

router = APIRouter()
settings = get_settings()


@router.post("/tweets", response_model=OperationResponse)
async def create_tweet_route(
    tweet: TweetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_tweet = await create_tweet(
        db, current_user.id, tweet.tweet_data, tweet.tweet_media_ids
    )
    return OperationResponse(result=True, tweet_id=new_tweet.id)


@router.post("/medias", response_model=OperationResponse)
async def upload_media(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    media_folder = settings.media_folder
    os.makedirs(media_folder, exist_ok=True)
    file_path = os.path.join(media_folder, f"{uuid4()}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
    media = await create_media(db, file_path)
    return OperationResponse(result=True, media_id=media.id)


@router.delete("/tweets/{tweet_id}", response_model=OperationResponse)
async def delete_tweet_route(
    tweet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await delete_tweet(db, tweet_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Твит не найден")
    return OperationResponse(result=True)


@router.post("/tweets/{tweet_id}/likes", response_model=OperationResponse)
async def like_tweet_route(
    tweet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await like_tweet(db, tweet_id, current_user)
    return OperationResponse(result=True)


@router.delete("/tweets/{tweet_id}/likes", response_model=OperationResponse)
async def unlike_tweet_route(
    tweet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await unlike_tweet(db, tweet_id, current_user)
    return OperationResponse(result=True)


@router.post("/users/{user_id}/follow", response_model=OperationResponse)
async def follow_user_route(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await follow_user(db, user_id, current_user)
    return OperationResponse(result=True)


@router.delete("/users/{user_id}/follow", response_model=OperationResponse)
async def unfollow_user_route(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await unfollow_user(db, user_id, current_user)
    return OperationResponse(result=True)


@router.get("/tweets", response_model=TweetsResponse)
async def get_tweets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tweets = await get_feed(db, current_user)
    response_tweets = []
    for t in tweets:
        attachments = [f"/{m.file_path}" for m in t.medias]
        likes = [{"user_id": u.id, "name": u.name} for u in t.likes]
        author = {"id": t.author.id, "name": t.author.name}
        response_tweets.append(
            {
                "id": t.id,
                "content": t.content,
                "created_at": t.created_at,
                "attachments": attachments,
                "author": author,
                "likes": likes,
            }
        )
    return {"result": True, "tweets": response_tweets}


@router.get("/users/me", response_model=UserResponse)
async def get_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await get_user_profile(db, current_user.id)
    followers = [{"id": f.id, "name": f.name} for f in profile.followers]
    following = [{"id": f.id, "name": f.name} for f in profile.following]
    return {
        "result": True,
        "user": {
            "id": profile.id,
            "name": profile.name,
            "followers": followers,
            "following": following,
        },
    }


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    profile = await get_user_profile(db, user_id)
    followers = [{"id": f.id, "name": f.name} for f in profile.followers]
    following = [{"id": f.id, "name": f.name} for f in profile.following]
    return {
        "result": True,
        "user": {
            "id": profile.id,
            "name": profile.name,
            "followers": followers,
            "following": following,
        },
    }
