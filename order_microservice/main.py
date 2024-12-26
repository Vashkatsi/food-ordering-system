import uvicorn
from fastapi import FastAPI

from infrastructure.http.order_controller import order_router

app = FastAPI()
app.include_router(order_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
