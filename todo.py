from dataclasses import dataclass
from litestar import get, post
from litestar.exceptions import HTTPException
from litestar.handlers import HTTPRouteHandler, put



@dataclass
class Todo:
    id: int
    title: str
    description: str
    completed: bool


@dataclass
class TodoUpdate:
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


todos: list[Todo] = [
    Todo(id=1, title="Buy groceries", description="Buy groceries", completed=False),
    Todo(id=2, title="Buy a new car", description="Buy a new car", completed=False),
    Todo(id=3, title="Buy a new house", description="Buy a new house", completed=True),
]


def get_todo_by_title(title: str) -> Todo | None:
    return next((item for item in todos if item.title == title), None)



@get("/")
async def read_root(completed: bool | None = None) -> list[Todo]:
    if completed is None:
        return todos
    return [item for item in todos if item.completed == completed]


@post("/")
async def create_todo(data: Todo) -> Todo:
    new_todo = Todo(
        id=len(todos) + 1,
        title=data.title,
        description=data.description,
        completed=False,
    )
    todos.append(new_todo)
    return new_todo

@put("/{item_title:str}")
async def update_todo(item_title: str, data: TodoUpdate) -> Todo:
    todo = get_todo_by_title(item_title)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    if data.title is not None:
        todo.title = data.title
    if data.description is not None:
        todo.description = data.description
    if data.completed is not None:
        todo.completed = data.completed
    return todo



def setup_routes() -> list[HTTPRouteHandler]:
    return [
        read_root,
        create_todo,
        update_todo,
    ]
