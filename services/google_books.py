import httpx2

from config import settings
from enums import BookGenre
from schemas.books import BookSearchResult

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"


def _convert_google_category_to_genre(main_category: str | None) -> BookGenre:
    if main_category is None:
        return BookGenre.OTHER

    normalized_category = main_category.lower()

    if (
        "comics" in normalized_category
        or "manga" in normalized_category
        or "graphic novels" in normalized_category
    ):
        return BookGenre.MANGA

    if "fiction" in normalized_category:
        return BookGenre.NOVEL

    if (
        "business" in normalized_category
        or "economics" in normalized_category
        or "finance" in normalized_category
    ):
        return BookGenre.BUSINESS

    if "self-help" in normalized_category or "self help" in normalized_category:
        return BookGenre.SELF_HELP

    if (
        "computers" in normalized_category
        or "technology" in normalized_category
        or "engineering" in normalized_category
    ):
        return BookGenre.TECHNOLOGY

    if (
        "history" in normalized_category
        or "philosophy" in normalized_category
        or "social science" in normalized_category
        or "psychology" in normalized_category
        or "religion" in normalized_category
        or "biography" in normalized_category
    ):
        return BookGenre.HUMANITIES

    if (
        "science" in normalized_category
        or "mathematics" in normalized_category
        or "medical" in normalized_category
        or "nature" in normalized_category
    ):
        return BookGenre.SCIENCE

    return BookGenre.OTHER


def _parse_google_book(item: dict) -> BookSearchResult | None:
    external_id = item.get("id")
    volume_info = item.get("volumeInfo", {})

    title = volume_info.get("title")
    authors = volume_info.get("authors", [])

    main_category = volume_info.get("mainCategory")
    categories = volume_info.get("categories", [])
    category = main_category

    image_links = volume_info.get("imageLinks", {})
    if "small" in image_links:
        cover_image_url = image_links.get("small")
    elif "thumbnail" in image_links:
        cover_image_url = image_links.get("thumbnail")
    elif "smallThumbnail" in image_links:
        cover_image_url = image_links.get("smallThumbnail")
    else:
        cover_image_url = None

    if not category and categories:
        category = categories[0]

    genre = _convert_google_category_to_genre(category)

    industry_identifiers = volume_info.get("industryIdentifiers", [])
    isbn = None
    for industry_data in industry_identifiers:
        if industry_data.get("type") == "ISBN_13":
            isbn = industry_data.get("identifier")
            break
    if not external_id or not title or not authors or not isbn:
        return None
    author = " / ".join(authors)

    search_result = BookSearchResult(
        external_id=external_id,
        title=title,
        author=author,
        isbn=isbn,
        genre=genre,
        cover_image_url=cover_image_url,
    )
    return search_result


def search_google_books(
    query: str,
) -> list[BookSearchResult]:

    response = httpx2.get(
        GOOGLE_BOOKS_API_URL,
        params={"q": query},
        headers={"x-goog-api-key": settings.google_books_api_key},
        timeout=10.0,
    )

    response.raise_for_status()
    response_data = response.json()
    items = response_data.get("items", [])
    search_results: list[BookSearchResult] = []
    for item in items:
        search_result = _parse_google_book(item)
        if search_result is None:
            continue

        search_results.append(search_result)

    return search_results


def get_google_book(external_id: str) -> BookSearchResult | None:
    response = httpx2.get(
        f"{GOOGLE_BOOKS_API_URL}/{external_id}",
        headers={"x-goog-api-key": settings.google_books_api_key},
        timeout=10.0,
    )

    response.raise_for_status()
    response_data = response.json()

    return _parse_google_book(response_data)
