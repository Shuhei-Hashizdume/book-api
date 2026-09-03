from fastapi import FastAPI

app = FastAPI()

books = [
    {
        "id": 1,
        "title": "GANTZ 1",
        "author": "奥 浩哉",
        "isbn": "978-4-08-876105-3",
    },
    {
        "id": 2,
        "title": "嫌われる勇気",
        "author": "岸見 一郎、古賀 史健",
        "isbn": "978-4-478-02581-9",
    },
    {
        "id": 3,
        "title": "メモの魔力",
        "author": "前田 裕二",
        "isbn": "978-4-344-03408-2",
    },
]


@app.get("/")
def read_root():
    return {"message": "book-api"}


@app.get("/books/1")
def read_book():
    return books[0]


@app.get("/books")
def read_books():
    return books
