from uuid import uuid4

from factory import (
    Factory,
    Faker,
    LazyAttribute,
    LazyFunction,
    Sequence,
    SubFactory,
)

from app.schemas import (
    OperationResponse,
    TweetCreate,
    TweetResponse,
    TweetsResponse,
    UserProfile,
    UserResponse,
)


class TweetCreateFactory(Factory):
    class Meta:
        model = TweetCreate

    tweet_data = Faker("text", max_nb_chars=1024)
    tweet_media_ids = LazyFunction(lambda x: [])


class OperationResponseTweetFactory(Factory):
    class Meta:
        model = OperationResponse

    result = True
    tweet_id = Sequence(lambda n: n + 1)
    media_id = None


class OperationResponseMediaFactory(Factory):
    class Meta:
        model = OperationResponse

    result = True
    tweet_id = None
    media_id = Sequence(lambda n: n + 100)


class TweetResponseFactory(Factory):
    class Meta:
        model = TweetResponse

    id = Sequence(lambda n: n + 1)
    content = Faker("text", max_nb_chars=1024)
    created_at = Faker("date_time_this_year")
    attachments = LazyAttribute(
        lambda x: [f"/media/{uuid4()}_test.jpg" for _ in range(2)]
    )
    author = LazyAttribute(lambda x: {"id": 1, "name": Faker("name")})
    likes = LazyFunction(
        lambda x: [{"user_id": i + 2, "name": Faker("name")} for i in range(3)]
    )


class TweetsResponseFactory(Factory):
    class Meta:
        model = TweetsResponse

    result = True
    tweets = [SubFactory(TweetResponseFactory) for _ in range(3)]


class UserProfileFactory(Factory):
    class Meta:
        model = UserProfile

    id = Sequence(lambda n: n + 1)
    name = Faker("name")
    followers = LazyAttribute(
        lambda o: [{"id": 100 + i, "name": Faker("name")} for i in range(3)]
    )
    following = LazyAttribute(
        lambda o: [{"id": 200 + i, "name": Faker("name")} for i in range(2)]
    )


class UserResponseFactory(Factory):
    class Meta:
        model = UserResponse

    result = True
    user = SubFactory(UserProfileFactory)
