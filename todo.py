from dataclasses import dataclass
from sqlite3 import IntegrityError
from litestar.datastructures import State
from typing import Sequence
from litestar import get, post
from litestar.exceptions import ClientException, NotFoundException
from litestar.handlers import HTTPRouteHandler, put
from litestar.params import FromPath, FromQuery
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from litestar.status_codes import HTTP_409_CONFLICT


from db import TodoItem, sessionmaker



@dataclass
class Todo:
    title: str
    description: str
    completed: bool

type TodoCollectionType = list[Todo]
@dataclass
class TodoUpdate:
    title: str | None = None
    description: str | None = None
    completed: bool | None = None






def serialize_todo(todo: TodoItem) -> Todo: 
    return Todo(
        title=todo.title,
        description=todo.description,
        completed=todo.completed
    )


async def get_todo_by_title(todo_name: FromPath[str], session: AsyncSession) -> TodoItem:
    query = select(TodoItem).where(TodoItem.title == todo_name)
    result = await session.execute(query)
    try:
        return result.scalar_one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"TODO {todo_name!r} not found") from e



async def get_todo_list(done: FromQuery[bool | None], session: AsyncSession) -> Sequence[TodoItem]:
    query = select(TodoItem)
    if done is not None:
        query = query.where(TodoItem.completed.is_(done))

    result = await session.execute(query)
    return result.scalars().all()






@get("/")
async def get_list(state: State, done: FromQuery[bool | None] = None) -> TodoCollectionType:
    async with sessionmaker(bind=state.engine) as session:
        return [serialize_todo(todo) for todo in await get_todo_list(done, session)]


@post("/")
async def add_item(data: Todo, state: State) -> Todo:
    new_todo = TodoItem(title=data.title, description=data.description, completed=data.completed)
    async with sessionmaker(bind=state.engine) as session:
        try:
            async with session.begin():
                session.add(new_todo)
        except IntegrityError as e:
            raise ClientException(
                status_code=HTTP_409_CONFLICT,
                detail=f"TODO {new_todo.title!r} already exists",
            ) from e

    return serialize_todo(new_todo)


@put("/{item_title:str}")
async def update_item(item_title: FromPath[str], data: Todo, state: State) -> Todo:
    async with sessionmaker(bind=state.engine) as session, session.begin():
        todo_item = await get_todo_by_title(item_title, session)
        todo_item.title = data.title
        todo_item.description = data.description
        todo_item.completed = data.completed
    return serialize_todo(todo_item)


def setup_routes() -> list[HTTPRouteHandler]:
    return [
     get_list,
     add_item,
     update_item  
    ]
