from litestar import Litestar
import uvicorn
from db import db_connection
from todo import setup_routes


routes = setup_routes()
app = Litestar(routes, lifespan=[db_connection])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
