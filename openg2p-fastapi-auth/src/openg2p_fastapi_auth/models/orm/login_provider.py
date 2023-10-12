from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import JSON, Boolean, DateTime, String, select
from sqlalchemy import Enum as SaEnum
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column


class LoginProviderTypes(Enum):
    oauth2_auth_code = "oauth2_auth_code"


class LoginProvider(BaseORMModel):
    __tablename__ = "login_providers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    type: Mapped[LoginProviderTypes] = mapped_column(SaEnum(LoginProviderTypes))

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
    async def get_login_providers(cls) -> List["LoginProvider"]:
        response = []
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = select(cls).order_by(cls.id.asc())

            result = await session.execute(stmt)

            response = list(result.scalars())
        return response

    @classmethod
    async def get_login_provider_by_id(cls, id: int) -> "LoginProvider":
        result = None
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            result = await session.get(cls, id)

        return result

    @classmethod
    async def get_login_provider_from_iss(cls, iss: str) -> "LoginProvider":
        providers = await cls.get_login_providers()
        for lp in providers:
            if lp.type == LoginProviderTypes.oauth2_auth_code:
                if iss in lp.authorization_parameters.get("token_endpoint", ""):
                    return lp
            else:
                raise NotImplementedError()
        return None
