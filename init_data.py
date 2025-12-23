import asyncio

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import settings
from app.models import Tweet, User, tweet_likes, user_follows

database_url = (
    f"postgresql+asyncpg://"
    f"{settings.postgres_user}:"
    f"{settings.postgres_password.get_secret_value()}"
    f"@{settings.postgres_host}:{settings.postgres_port}/"
    f"{settings.postgres_db}"
)


async def seed_data() -> None:
    engine = create_async_engine(database_url)
    async with AsyncSession(engine) as session:
        async with session.begin():
            result = await session.execute(select(User).limit(1))
            if result.scalar_one_or_none() is not None:
                print("Данные уже есть в БД. Пропускаем.")
                return

            stmt = (
                insert(User)
                .values(
                    [
                        {"name": "Test User 1", "api_key": "test"},
                        {"name": "Test User 2", "api_key": "test2"},
                        {"name": "Test User 3", "api_key": "test3"},
                    ]
                )
                .returning(User.id)
            )
            result = await session.execute(stmt)
            user_ids = result.scalars().all()
            user1_id, user2_id, user3_id = user_ids

            stmt = (
                insert(Tweet)
                .values(
                    [
                        {
                            "content": "Привет, это первый твит!",
                            "author_id": user1_id,
                        },
                        {
                            "content": "Второй твит с упоминанием.",
                            "author_id": user2_id,
                        },
                    ]
                )
                .returning(Tweet.id)
            )
            result = await session.execute(stmt)
            tweet_ids = result.scalars().all()
            tweet1_id, tweet2_id = tweet_ids

            await session.execute(
                insert(user_follows).values(
                    follower_id=user1_id, followed_id=user2_id
                )
            )

            await session.execute(
                insert(tweet_likes).values(
                    user_id=user3_id, tweet_id=tweet1_id
                )
            )
            await session.commit()
            print("Тестовые данные успешно добавлены!")


if __name__ == "__main__":
    asyncio.run(seed_data())
