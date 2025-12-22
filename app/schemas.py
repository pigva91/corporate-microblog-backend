from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TweetCreate(BaseModel):
    tweet_data: str = Field(description="Содержимое твита")
    tweet_media_ids: Optional[List[int]] = Field(description="ID медиафайлов")


class TweetResponse(BaseModel):
    id: int = Field(description="ID твита")
    content: str = Field(description="Содержимое твита")
    created_at: datetime = Field(description="Дата создания твита")
    attachments: List[str] = Field(description="Ссылки на attachments")
    author: dict = Field(description="Автор: {'id': int, 'name': str}")
    likes: List[dict] = Field(
        description="Лайки: [{'user_id': int, 'name': str}]"
    )

    model_config = ConfigDict(from_attributes=True)


class UserProfile(BaseModel):
    id: int = Field(description="ID пользователя")
    name: str = Field(description="Имя пользователя")
    followers: List[dict] = Field(
        description="Фолловеры: [{'id': int, 'name': str}]"
    )
    following: List[dict] = Field(
        description="Фолловинг: [{'id': int, 'name': str}]"
    )

    model_config = ConfigDict(from_attributes=True)


class OperationResponse(BaseModel):
    result: bool = Field(description="Результат операции")
    tweet_id: Optional[int] = Field(
        default=None, description="ID твита, если применимо"
    )
    media_id: Optional[int] = Field(
        default=None, description="ID медиа, если применимо"
    )

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    result: bool = Field(description="Всегда False для ошибок")
    error_type: str = Field(description="Тип ошибки")
    error_message: str = Field(description="Сообщение об ошибке")

    model_config = ConfigDict(from_attributes=True)


class TweetsResponse(BaseModel):
    result: bool
    tweets: List[TweetResponse]


class UserResponse(BaseModel):
    result: bool
    user: UserProfile
