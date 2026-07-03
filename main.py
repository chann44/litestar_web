from litestar import Litestar
import uvicorn
from todo import setup_routes


routes = setup_routes()
app = Litestar(routes)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
