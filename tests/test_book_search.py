import httpx2
import pytest
from fastapi.testclient import TestClient

from enums import BookGenre
from main import app
from routers import books
from schemas.books import BookSearchResult
from services import google_books

client = TestClient(app)


@pytest.fixture(autouse=True)
def use_test_google_books_api_key(monkeypatch):
    monkeypatch.setattr(
        google_books.settings,
        "google_books_api_key",
        "test-api-key",
    )


def test_search_books_returns_results(monkeypatch):
    def fake_search_google_books(query: str) -> list[BookSearchResult]:
        assert query == "GANTZ"
        return [
            BookSearchResult(
                external_id="google-book-id",
                title="GANTZ",
                author="奥浩哉",
                isbn="9784086196123",
                genre=BookGenre.MANGA,
                cover_image_url="https://example.com/gantz-small.jpg",
            )
        ]

    monkeypatch.setattr(
        books,
        "search_google_books",
        fake_search_google_books,
    )

    response = client.get(
        "/books/search",
        params={"q": " GANTZ "},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "external_id": "google-book-id",
            "title": "GANTZ",
            "author": "奥浩哉",
            "isbn": "9784086196123",
            "genre": "manga",
            "cover_image_url": "https://example.com/gantz-small.jpg",
        }
    ]


def test_search_books_requires_query():
    response = client.get("/books/search")

    assert response.status_code == 422


@pytest.mark.parametrize("query", ["", "  "])
def test_search_books_rejects_blank_query(query, monkeypatch):
    def fake_search_google_books(query: str) -> list[BookSearchResult]:
        return []

    monkeypatch.setattr(books, "search_google_books", fake_search_google_books)

    response = client.get(
        "/books/search",
        params={"q": query},
    )

    assert response.status_code == 422


def test_search_books_returns_502_when_google_returns_error(monkeypatch):
    def fake_search_google_books(query: str) -> None:
        request = httpx2.Request(
            "GET",
            "https://www.googleapis.com/books/v1/volumes",
        )
        response = httpx2.Response(
            status_code=500,
            request=request,
        )

        raise httpx2.HTTPStatusError(
            "Google Books API error",
            request=request,
            response=response,
        )

    monkeypatch.setattr(
        books,
        "search_google_books",
        fake_search_google_books,
    )

    response = client.get(
        "/books/search",
        params={"q": "GANTZ"},
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "書籍検索サービスから正常な応答を取得できませんでした。"
    }


def test_search_books_returns_504_when_google_times_out(monkeypatch):
    def fake_search_google_books(query: str) -> None:
        request = httpx2.Request(
            "GET",
            "https://www.googleapis.com/books/v1/volumes",
        )

        raise httpx2.TimeoutException(
            "Google Books API timeout",
            request=request,
        )

    monkeypatch.setattr(
        books,
        "search_google_books",
        fake_search_google_books,
    )

    response = client.get(
        "/books/search",
        params={"q": "GANTZ"},
    )

    assert response.status_code == 504
    assert response.json() == {
        "detail": "書籍検索サービスから時間内に応答がありませんでした。"
    }


def test_search_books_returns_502_when_google_connection_fails(monkeypatch):
    def fake_search_google_books(query: str) -> None:
        request = httpx2.Request(
            "GET",
            "https://www.googleapis.com/books/v1/volumes",
        )

        raise httpx2.RequestError(
            "Google Books API connection error",
            request=request,
        )

    monkeypatch.setattr(
        books,
        "search_google_books",
        fake_search_google_books,
    )

    response = client.get(
        "/books/search",
        params={"q": "GANTZ"},
    )

    assert response.status_code == 502
    assert response.json() == {"detail": "書籍検索サービスへ接続できませんでした。"}


def test_search_google_books_formats_results(monkeypatch):
    def fake_get(url, params, headers, timeout):
        assert url == google_books.GOOGLE_BOOKS_API_URL
        assert params == {"q": "GANTZ", "maxResults": 40}
        assert "x-goog-api-key" in headers
        assert timeout == 10.0

        request = httpx2.Request("GET", url)
        return httpx2.Response(
            status_code=200,
            request=request,
            json={
                "items": [
                    {
                        "id": "google-book-id",
                        "volumeInfo": {
                            "title": "GANTZ",
                            "authors": ["著者A", "著者B"],
                            "categories": ["Comics & Graphic Novels"],
                            "industryIdentifiers": [
                                {
                                    "type": "ISBN_10",
                                    "identifier": "1234567890",
                                },
                                {
                                    "type": "ISBN_13",
                                    "identifier": "9784086196123",
                                },
                            ],
                        },
                    }
                ]
            },
        )

    monkeypatch.setattr(
        google_books.httpx2,
        "get",
        fake_get,
    )

    results = google_books.search_google_books("GANTZ")

    assert results == [
        BookSearchResult(
            external_id="google-book-id",
            title="GANTZ",
            author="著者A / 著者B",
            isbn="9784086196123",
            genre=BookGenre.MANGA,
            cover_image_url=None,
        )
    ]


@pytest.mark.parametrize(
    ("image_links", "expected_cover_image_url"),
    [
        (
            {
                "small": "https://example.com/small.jpg",
                "thumbnail": "https://example.com/thumbnail.jpg",
                "smallThumbnail": "https://example.com/small-thumbnail.jpg",
            },
            "https://example.com/small.jpg",
        ),
        (
            {
                "thumbnail": "https://example.com/thumbnail.jpg",
                "smallThumbnail": "https://example.com/small-thumbnail.jpg",
            },
            "https://example.com/thumbnail.jpg",
        ),
        (
            {
                "smallThumbnail": "https://example.com/small-thumbnail.jpg",
            },
            "https://example.com/small-thumbnail.jpg",
        ),
        ({}, None),
    ],
)
def test_parse_google_book_selects_cover_image_url(
    image_links,
    expected_cover_image_url,
):
    item = {
        "id": "google-book-id",
        "volumeInfo": {
            "title": "テスト本",
            "authors": ["テスト著者"],
            "industryIdentifiers": [
                {
                    "type": "ISBN_13",
                    "identifier": "9780000000001",
                }
            ],
            "imageLinks": image_links,
        },
    }

    result = google_books._parse_google_book(item)

    assert result is not None
    assert result.cover_image_url == expected_cover_image_url


def test_search_google_books_returns_empty_list_when_no_results(monkeypatch):
    def fake_get(url, params, headers, timeout):
        request = httpx2.Request("GET", url)
        return httpx2.Response(
            status_code=200,
            request=request,
            json={
                "totalItems": 0,
            },
        )

    monkeypatch.setattr(
        google_books.httpx2,
        "get",
        fake_get,
    )

    results = google_books.search_google_books("存在しない本")

    assert results == []


def test_search_google_books_excludes_incomplete_results(monkeypatch):
    def fake_get(url, params, headers, timeout):
        request = httpx2.Request("GET", url)
        return httpx2.Response(
            status_code=200,
            request=request,
            json={
                "items": [
                    {
                        "volumeInfo": {
                            "title": "IDなし",
                            "authors": ["著者"],
                            "industryIdentifiers": [
                                {
                                    "type": "ISBN_13",
                                    "identifier": "9780000000001",
                                }
                            ],
                        }
                    },
                    {
                        "id": "no-title",
                        "volumeInfo": {
                            "authors": ["著者"],
                            "industryIdentifiers": [
                                {
                                    "type": "ISBN_13",
                                    "identifier": "9780000000002",
                                }
                            ],
                        },
                    },
                    {
                        "id": "no-authors",
                        "volumeInfo": {
                            "title": "著者なし",
                            "industryIdentifiers": [
                                {
                                    "type": "ISBN_13",
                                    "identifier": "9780000000003",
                                }
                            ],
                        },
                    },
                    {
                        "id": "no-isbn-13",
                        "volumeInfo": {
                            "title": "ISBN13なし",
                            "authors": ["著者"],
                            "industryIdentifiers": [
                                {
                                    "type": "ISBN_10",
                                    "identifier": "0000000004",
                                }
                            ],
                        },
                    },
                    {
                        "id": "complete-book",
                        "volumeInfo": {
                            "title": "正常な本",
                            "authors": ["著者"],
                            "industryIdentifiers": [
                                {
                                    "type": "ISBN_13",
                                    "identifier": "9780000000005",
                                }
                            ],
                        },
                    },
                ]
            },
        )

    monkeypatch.setattr(
        google_books.httpx2,
        "get",
        fake_get,
    )

    results = google_books.search_google_books("検索語")

    assert results == [
        BookSearchResult(
            external_id="no-isbn-13",
            title="ISBN13なし",
            author="著者",
            isbn=None,
            genre=BookGenre.OTHER,
            cover_image_url=None,
        ),
        BookSearchResult(
            external_id="complete-book",
            title="正常な本",
            author="著者",
            isbn="9780000000005",
            genre=BookGenre.OTHER,
            cover_image_url=None,
        )
    ]


def test_search_google_books_raises_for_error_response(monkeypatch):
    def fake_get(url, params, headers, timeout):
        request = httpx2.Request("GET", url)
        return httpx2.Response(
            status_code=500,
            request=request,
        )

    monkeypatch.setattr(
        google_books.httpx2,
        "get",
        fake_get,
    )

    with pytest.raises(httpx2.HTTPStatusError):
        google_books.search_google_books("GANTZ")


def test_get_google_books(monkeypatch):

    def fake_get(url, headers, timeout):
        assert url == f"{google_books.GOOGLE_BOOKS_API_URL}/abc123"

        assert headers["x-goog-api-key"] == "test-api-key"
        assert timeout == 10.0

        request = httpx2.Request("GET", url)
        return httpx2.Response(
            status_code=200,
            request=request,
            json={
                "id": "abc123",
                "volumeInfo": {
                    "title": "テスト本",
                    "authors": ["著者A", "著者B"],
                    "mainCategory": "Business & Economics",
                    "industryIdentifiers": [
                        {
                            "type": "ISBN_13",
                            "identifier": "9780000000001",
                        }
                    ],
                },
            },
        )

    monkeypatch.setattr(
        google_books.httpx2,
        "get",
        fake_get,
    )

    result = google_books.get_google_book("abc123")
    assert result == BookSearchResult(
        external_id="abc123",
        title="テスト本",
        author="著者A / 著者B",
        isbn="9780000000001",
        genre=BookGenre.BUSINESS,
        cover_image_url=None,
    )


def test_get_google_book_raises_for_error_response(monkeypatch):
    def fake_get(url, headers, timeout):
        assert url == f"{google_books.GOOGLE_BOOKS_API_URL}/error-book-id"
        assert headers["x-goog-api-key"] == "test-api-key"
        assert timeout == 10.0

        request = httpx2.Request("GET", url)
        return httpx2.Response(
            status_code=500,
            request=request,
        )

    monkeypatch.setattr(
        google_books.httpx2,
        "get",
        fake_get,
    )

    with pytest.raises(httpx2.HTTPStatusError):
        google_books.get_google_book("error-book-id")


@pytest.mark.parametrize(
    ("main_category", "expected_genre"),
    [
        ("Comics & Graphic Novels / Manga", BookGenre.MANGA),
        ("Fiction", BookGenre.NOVEL),
        ("Business & Economics", BookGenre.BUSINESS),
        ("Self-Help", BookGenre.SELF_HELP),
        ("Computers", BookGenre.TECHNOLOGY),
        ("Social Science", BookGenre.HUMANITIES),
        ("Science", BookGenre.SCIENCE),
        ("Unknown Category", BookGenre.OTHER),
        (None, BookGenre.OTHER),
    ],
)
def test_convert_google_category_to_genre(
    main_category,
    expected_genre,
):
    result = google_books._convert_google_category_to_genre(main_category)

    assert result == expected_genre


@pytest.mark.parametrize(
    "identifiers", [[], [{"type": "ISBN_10", "identifier": "0000000004"}]]
)
def test_get_google_book_returns_book_without_isbn_13(monkeypatch, identifiers):
    def fake_get(url, headers, timeout):
        assert url == f"{google_books.GOOGLE_BOOKS_API_URL}/no-isbn-book"
        return httpx2.Response(
            status_code=200,
            request=httpx2.Request("GET", url),
            json={
                "id": "no-isbn-book",
                "volumeInfo": {
                    "title": "ISBNなしの本",
                    "authors": ["テスト著者"],
                    "industryIdentifiers": identifiers,
                },
            },
        )

    monkeypatch.setattr(google_books.httpx2, "get", fake_get)

    result = google_books.get_google_book("no-isbn-book")
    assert result == BookSearchResult(
        external_id="no-isbn-book",
        title="ISBNなしの本",
        author="テスト著者",
        isbn=None,
        genre=BookGenre.OTHER,
        cover_image_url=None,
    )
