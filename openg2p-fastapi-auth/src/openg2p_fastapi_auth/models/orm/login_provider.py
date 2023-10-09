from datetime import datetime
from typing import Any, Optional

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import JSON, Boolean, DateTime, String, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column


class LoginProvider(BaseORMModel):
    __tablename__ = "login_providers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    type: Mapped[str] = mapped_column(String())

    description: Mapped[Optional[str]] = mapped_column(String())

    login_button_text: Mapped[str] = mapped_column(String())
    login_button_image_url: Mapped[str] = mapped_column(String())

    authorization_parameters: Mapped[dict[str, Any]] = mapped_column(JSON(), default={})

    active: Mapped[bool] = mapped_column(Boolean())

    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(), default=datetime.utcnow
    )

    @classmethod
    async def get_login_providers(cls):
        response = []
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = select(cls).order_by(cls.id.asc())

            result = await session.execute(stmt)

            response = list(result.scalars())
        return response
