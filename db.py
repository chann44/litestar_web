from contextlib import asynccontextmanager
from litestar import Litestar
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine



class Base(DeclarativeBase): ...


class TodoItem(Base):
    __tablename__ = "todo_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)



@asynccontextmanager
async def db_connection(app: Litestar) -> AsyncGenerator[None, None]:
        engine = getattr(app.state, "engine", None)
        if engine is None: 
            engine = create_async_engine("sqlite+aiosqlite:///todo.sqlite", echo=True)
            app.state.engine = engine
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        try:
            yield
        finally:
            await engine.dispose()

sessionmaker = async_sessionmaker(expire_on_commit=False)




