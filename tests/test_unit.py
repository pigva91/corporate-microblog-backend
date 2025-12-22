import pytest
from fastapi import HTTPException

from app.crud import (
    create_media,
    create_tweet,
    delete_tweet,
    follow_user,
    get_feed,
    get_user_by_api_key,
    get_user_profile,
    like_tweet,
    unfollow_user,
    unlike_tweet,
)
from app.models import Tweet, User


@pytest.mark.asyncio
async def test_create_tweet(db_session, test_user_id):
    tweet = await create_tweet(db_session, test_user_id, "Тест твит")
    assert tweet.content == "Тест твит"
    assert tweet.author_id == test_user_id


@pytest.mark.asyncio
async def test_create_tweet_with_media(db_session, test_user_id):
    media = await create_media(db_session, "/tmp/test.jpg")
    assert media.tweet_id is None

    tweet = await create_tweet(
        db_session, test_user_id, "Твит с картинкой", media_ids=[media.id]
    )
    assert tweet.content == "Твит с картинкой"
    assert tweet.author_id == test_user_id
    assert len(tweet.medias) == 1
    assert tweet.medias[0].id == media.id
    assert tweet.medias[0].tweet_id == tweet.id


@pytest.mark.asyncio
async def test_delete_tweet_success(db_session, test_user_id):
    tweet = await create_tweet(db_session, test_user_id, "To delete")
    deleted = await delete_tweet(db_session, tweet.id, test_user_id)
    assert deleted is True

    result = await db_session.get(Tweet, tweet.id)
    assert result is None


@pytest.mark.asyncio
async def test_delete_tweet_not_owner(db_session, test_user, another_user):
    tweet = await create_tweet(db_session, test_user.id, "Protected tweet")
    deleted = await delete_tweet(db_session, tweet.id, another_user.id)
    assert deleted is False

    result = await db_session.get(Tweet, tweet.id)
    assert result is not None


@pytest.mark.asyncio
async def test_like_tweet(db_session, test_user_id):
    tweet = await create_tweet(db_session, test_user_id, "Like me")

    user = await db_session.get(User, test_user_id)
    assert user is not None

    await like_tweet(db_session, tweet.id, user)
    await db_session.refresh(tweet, attribute_names=["likes"])
    assert user in tweet.likes


@pytest.mark.asyncio
async def test_unlike_tweet(db_session, test_user_id):
    tweet = await create_tweet(db_session, test_user_id, "Unlike me")

    user = await db_session.get(User, test_user_id)
    await like_tweet(db_session, tweet.id, user)

    await unlike_tweet(db_session, tweet.id, user)
    await db_session.refresh(tweet, attribute_names=["likes"])
    assert user not in tweet.likes


@pytest.mark.asyncio
async def test_like_nonexistent_tweet(db_session, test_user):
    with pytest.raises(HTTPException):
        await like_tweet(db_session, 999999, test_user)


@pytest.mark.asyncio
async def test_follow_user(db_session, test_user_id, another_user_id):
    user = await db_session.get(User, test_user_id)
    target = await db_session.get(User, another_user_id)

    await follow_user(db_session, target.id, user)

    await db_session.refresh(target, attribute_names=["followers"])
    assert user in target.followers


@pytest.mark.asyncio
async def test_unfollow_user(db_session, test_user_id, another_user_id):
    user = await db_session.get(User, test_user_id)
    target = await db_session.get(User, another_user_id)

    await follow_user(db_session, target.id, user)
    await unfollow_user(db_session, target.id, user)

    await db_session.refresh(target, attribute_names=["followers"])
    assert user not in target.followers


@pytest.mark.asyncio
async def test_follow_self_fails(db_session, test_user_id):
    user = await db_session.get(User, test_user_id)
    with pytest.raises(HTTPException) as exc:
        await follow_user(db_session, user.id, user)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_get_user_profile(db_session, test_user_id):
    profile = await get_user_profile(db_session, test_user_id)
    assert profile.id == test_user_id
    assert isinstance(profile.followers, list)
    assert isinstance(profile.following, list)


@pytest.mark.asyncio
async def test_get_feed_empty(db_session, test_user_id):
    user = await db_session.get(User, test_user_id)
    await db_session.refresh(user, attribute_names=["following"])
    feed = await get_feed(db_session, user)
    assert feed == []


@pytest.mark.asyncio
async def test_get_feed_with_following(
    db_session, test_user_id, another_user_id
):
    user = await db_session.get(User, test_user_id)
    target = await db_session.get(User, another_user_id)

    await follow_user(db_session, target.id, user)
    await db_session.refresh(user, attribute_names=["following"])
    tweet = await create_tweet(db_session, target.id, "From followed user")
    feed = await get_feed(db_session, user)
    assert len(feed) == 1
    assert feed[0].id == tweet.id


@pytest.mark.asyncio
async def test_get_user_by_api_key(db_session, test_user_id):
    user = await db_session.get(User, test_user_id)
    found = await get_user_by_api_key(db_session, user.api_key)
    assert found.id == user.id
