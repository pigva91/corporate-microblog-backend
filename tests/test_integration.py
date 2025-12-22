import pytest


@pytest.mark.asyncio
async def test_create_tweet_with_media(async_client, test_user):
    media_response = await async_client.post(
        "/api/medias",
        files={"file": ("test.jpg", b"fake image", "image/jpeg")},
        headers={"api-key": test_user.api_key},
    )
    assert media_response.status_code == 200
    assert media_response.json()["result"] is True
    media_id = int(media_response.json()["media_id"])

    payload = {
        "tweet_data": "Мой первый твит с картинкой!",
        "tweet_media_ids": [media_id],
    }
    response = await async_client.post(
        "/api/tweets",
        json=payload,
        headers={"api-key": test_user.api_key},
    )
    assert response.status_code == 200
    assert response.json()["result"] is True


@pytest.mark.asyncio
async def test_get_tweets_empty_feed(async_client, test_user):
    response = await async_client.get(
        "/api/tweets", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    assert response.json() == {"result": True, "tweets": []}


@pytest.mark.asyncio
async def test_get_feed_with_following(async_client, test_user, another_user):
    tweet_response = await async_client.post(
        "/api/tweets",
        json={"tweet_data": "Твит от Бориса", "tweet_media_ids": []},
        headers={"api-key": another_user.api_key},
    )
    assert tweet_response.status_code == 200

    await async_client.post(
        f"/api/users/{another_user.id}/follow",
        headers={"api-key": test_user.api_key},
    )

    response = await async_client.get(
        "/api/tweets", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert len(data["tweets"]) == 1
    assert data["tweets"][0]["content"] == "Твит от Бориса"
    assert data["tweets"][0]["author"]["id"] == another_user.id


@pytest.mark.asyncio
async def test_delete_tweet(async_client, test_user):
    response = await async_client.post(
        "/api/tweets",
        json={"tweet_data": "Удаляемый твит", "tweet_media_ids": []},
        headers={"api-key": test_user.api_key},
    )
    tweet_id = response.json()["tweet_id"]

    delete_response = await async_client.delete(
        f"/api/tweets/{tweet_id}", headers={"api-key": test_user.api_key}
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["result"] is True


@pytest.mark.asyncio
async def test_delete_not_owner_tweet(async_client, test_user, another_user):
    response = await async_client.post(
        "/api/tweets",
        json={"tweet_data": "Чужой твит", "tweet_media_ids": []},
        headers={"api-key": another_user.api_key},
    )
    tweet_id = response.json()["tweet_id"]
    delete_response = await async_client.delete(
        f"/api/tweets/{tweet_id}", headers={"api-key": test_user.api_key}
    )
    assert delete_response.status_code == 404
    assert delete_response.json()["result"] is False


@pytest.mark.asyncio
async def test_like_and_unlike_tweet(async_client, test_user, another_user):
    tweet_response = await async_client.post(
        "/api/tweets",
        json={"tweet_data": "Лайкаемый твит", "tweet_media_ids": []},
        headers={"api-key": another_user.api_key},
    )
    tweet_id = tweet_response.json()["tweet_id"]

    like_response = await async_client.post(
        f"/api/tweets/{tweet_id}/likes", headers={"api-Key": test_user.api_key}
    )
    assert like_response.status_code == 200
    assert like_response.json()["result"] is True

    unlike_response = await async_client.delete(
        f"/api/tweets/{tweet_id}/likes",
        headers={"api-Key": test_user.api_key},
    )
    assert unlike_response.status_code == 200


@pytest.mark.asyncio
async def test_follow_and_unfollow(async_client, test_user, another_user):
    await async_client.post(
        f"/api/users/{another_user.id}/follow",
        headers={"api-Key": test_user.api_key},
    )
    me = await async_client.get(
        "/api/users/me", headers={"api-Key": test_user.api_key}
    )
    assert len(me.json()["user"]["following"]) == 1

    await async_client.delete(
        f"/api/users/{another_user.id}/follow",
        headers={"api-Key": test_user.api_key},
    )
    me_after = await async_client.get(
        "/api/users/me", headers={"api-Key": test_user.api_key}
    )
    assert len(me_after.json()["user"]["following"]) == 0


@pytest.mark.asyncio
async def test_get_profiles(async_client, test_user, another_user):
    response = await async_client.get(
        "/api/users/me", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert data["user"]["id"] == test_user.id
    assert data["user"]["name"] == test_user.name

    response = await async_client.get(
        f"/api/users/{another_user.id}", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["id"] == another_user.id
    assert data["user"]["name"] == another_user.name


@pytest.mark.asyncio
async def test_nonexistent_user(async_client, test_user):
    response = await async_client.get(
        "/api/users/999999", headers={"api-key": test_user.api_key}
    )
    assert response.status_code == 404
