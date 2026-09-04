from fastapi import FastAPI

from routers.books import router as books_router

app = FastAPI()
app.include_router(books_router)
