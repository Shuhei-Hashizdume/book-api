from fastapi import FastAPI

from routers.books import router as books_router
from routers.insights import router as insight_router
from routers.likes import router as likes_router
from routers.reading_posts import router as reading_posts_router
from routers.user_books import router as user_books_router
from routers.users import router as users_router

app = FastAPI()
app.include_router(books_router)
app.include_router(users_router)
app.include_router(user_books_router)
app.include_router(insight_router)
app.include_router(reading_posts_router)
app.include_router(likes_router)
