
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Category
from src.core.db.repository.base import ContentRepository


class CategoryRepository(ContentRepository):
    """Репозиторий для работы с моделью Category."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Category)