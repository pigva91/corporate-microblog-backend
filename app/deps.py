from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import get_user_by_api_key
from app.database import get_db

API_KEY_HEADER = Header(..., alias="api-key")


async def get_current_user(
    api_key: str = API_KEY_HEADER,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user
