from datetime import datetime, timezone

from fastapi.testclient import TestClient

from main import app
from models import Book, BookRating, Follow, ReadingPost

client = TestClient(app)


def test_read_recommended_timeline(registered_user, book_in_db, db_session):
    book = db_session.get(Book, book_in_db.id)
    assert book is not None
    book.cover_image_url = "https://example.com/recommended-book-cover.jpg"

    book_rating = BookRating(
        user_id=registered_user.id,
        book_id=book_in_db.id,
        recommendation_score=5,
    )
    db_session.add(book_rating)
    db_session.commit()
    db_session.refresh(book_rating)

    reading_post = ReadingPost(
        user_id=book_rating.user_id,
        book_id=book_rating.book_id,
        recommendation_score=book_rating.recommendation_score,
        recommendation_reason="タイムラインで紹介する本",
        is_public=True,
    )
    db_session.add(reading_post)
    db_session.commit()
    db_session.refresh(reading_post)

    try:
        response = client.get("/timeline/recommended")

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1

        timeline_post = response_data[0]
        assert timeline_post["reading_post_id"] == reading_post.id
        assert timeline_post["user_id"] == registered_user.id
        assert timeline_post["username"] == registered_user.username
        assert timeline_post["book_id"] == book_in_db.id
        assert timeline_post["title"] == book_in_db.title
        assert (
            timeline_post["cover_image_url"]
            == "https://example.com/recommended-book-cover.jpg"
        )
        assert timeline_post["recommendation_score"] == 5
        assert timeline_post["recommendation_reason"] == "タイムラインで紹介する本"
        assert timeline_post["created_at"] is not None
    finally:
        db_session.delete(reading_post)
        db_session.flush()
        db_session.delete(book_rating)
        db_session.commit()


def test_recommended_timeline_excludes_private_posts(
    registered_user, other_user, book_in_db, db_session
):
    public_book_rating = BookRating(
        user_id=registered_user.id,
        book_id=book_in_db.id,
        recommendation_score=5,
    )
    private_book_rating = BookRating(
        user_id=other_user.id,
        book_id=book_in_db.id,
        recommendation_score=4,
    )
    db_session.add_all([public_book_rating, private_book_rating])
    db_session.commit()
    db_session.refresh(public_book_rating)
    db_session.refresh(private_book_rating)

    public_post = ReadingPost(
        user_id=public_book_rating.user_id,
        book_id=public_book_rating.book_id,
        recommendation_score=public_book_rating.recommendation_score,
        recommendation_reason="公開投稿",
        is_public=True,
    )
    private_post = ReadingPost(
        user_id=private_book_rating.user_id,
        book_id=private_book_rating.book_id,
        recommendation_score=private_book_rating.recommendation_score,
        recommendation_reason="非公開投稿",
        is_public=False,
    )
    db_session.add_all([public_post, private_post])
    db_session.commit()
    db_session.refresh(public_post)
    db_session.refresh(private_post)

    try:
        response = client.get("/timeline/recommended")

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1
        assert response_data[0]["reading_post_id"] == public_post.id
        assert response_data[0]["reading_post_id"] != private_post.id
    finally:
        db_session.delete(public_post)
        db_session.delete(private_post)
        db_session.flush()
        db_session.delete(public_book_rating)
        db_session.delete(private_book_rating)
        db_session.commit()


def test_recommended_timeline_orders_posts_by_newest(
    registered_user, other_user, book_in_db, db_session
):
    older_book_rating = BookRating(
        user_id=registered_user.id,
        book_id=book_in_db.id,
        recommendation_score=4,
    )
    newer_book_rating = BookRating(
        user_id=other_user.id,
        book_id=book_in_db.id,
        recommendation_score=5,
    )
    db_session.add_all([older_book_rating, newer_book_rating])
    db_session.commit()
    db_session.refresh(older_book_rating)
    db_session.refresh(newer_book_rating)

    older_post = ReadingPost(
        user_id=older_book_rating.user_id,
        book_id=older_book_rating.book_id,
        recommendation_score=older_book_rating.recommendation_score,
        recommendation_reason="古い公開投稿",
        is_public=True,
        created_at=datetime(2026, 9, 25, tzinfo=timezone.utc),
    )
    newer_post = ReadingPost(
        user_id=newer_book_rating.user_id,
        book_id=newer_book_rating.book_id,
        recommendation_score=newer_book_rating.recommendation_score,
        recommendation_reason="新しい公開投稿",
        is_public=True,
        created_at=datetime(2026, 9, 26, tzinfo=timezone.utc),
    )
    db_session.add_all([older_post, newer_post])
    db_session.commit()
    db_session.refresh(older_post)
    db_session.refresh(newer_post)

    try:
        response = client.get("/timeline/recommended")

        assert response.status_code == 200
        response_data = response.json()
        assert [post["reading_post_id"] for post in response_data] == [
            newer_post.id,
            older_post.id,
        ]
    finally:
        db_session.delete(newer_post)
        db_session.delete(older_post)
        db_session.flush()
        db_session.delete(newer_book_rating)
        db_session.delete(older_book_rating)
        db_session.commit()


def test_recommended_timeline_returns_empty_list_without_posts():
    response = client.get("/timeline/recommended")

    assert response.status_code == 200
    assert response.json() == []


def test_read_following_timeline(
    registered_user, other_user, book_in_db, db_session, access_token
):
    book = db_session.get(Book, book_in_db.id)
    assert book is not None
    book.cover_image_url = "https://example.com/following-book-cover.jpg"

    follow = Follow(
        follower_id=registered_user.id,
        followed_id=other_user.id,
    )
    book_rating = BookRating(
        user_id=other_user.id,
        book_id=book_in_db.id,
        recommendation_score=5,
    )
    db_session.add_all([follow, book_rating])
    db_session.commit()
    db_session.refresh(book_rating)

    reading_post = ReadingPost(
        user_id=book_rating.user_id,
        book_id=book_rating.book_id,
        recommendation_score=book_rating.recommendation_score,
        recommendation_reason="フォロー中タイムラインで紹介する本",
        is_public=True,
    )
    db_session.add(reading_post)
    db_session.commit()
    db_session.refresh(reading_post)

    try:
        response = client.get(
            "/timeline/following",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1

        timeline_post = response_data[0]
        assert timeline_post["reading_post_id"] == reading_post.id
        assert timeline_post["user_id"] == other_user.id
        assert timeline_post["username"] == other_user.username
        assert timeline_post["book_id"] == book_in_db.id
        assert timeline_post["title"] == book_in_db.title
        assert (
            timeline_post["cover_image_url"]
            == "https://example.com/following-book-cover.jpg"
        )
        assert timeline_post["recommendation_score"] == 5
        assert timeline_post["recommendation_reason"] == (
            "フォロー中タイムラインで紹介する本"
        )
        assert timeline_post["created_at"] is not None
    finally:
        db_session.delete(reading_post)
        db_session.flush()
        db_session.delete(book_rating)
        db_session.delete(follow)
        db_session.commit()


def test_following_timeline_excludes_private_posts(
    registered_user, other_user, book_in_db, db_session, access_token
):
    follow = Follow(
        follower_id=registered_user.id,
        followed_id=other_user.id,
    )
    book_rating = BookRating(
        user_id=other_user.id,
        book_id=book_in_db.id,
        recommendation_score=5,
    )
    db_session.add_all([follow, book_rating])
    db_session.commit()
    db_session.refresh(book_rating)

    private_post = ReadingPost(
        user_id=book_rating.user_id,
        book_id=book_rating.book_id,
        recommendation_score=book_rating.recommendation_score,
        recommendation_reason="フォロー先の非公開投稿",
        is_public=False,
    )
    db_session.add(private_post)
    db_session.commit()

    try:
        response = client.get(
            "/timeline/following",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        assert response.json() == []
    finally:
        db_session.delete(private_post)
        db_session.flush()
        db_session.delete(book_rating)
        db_session.delete(follow)
        db_session.commit()


def test_following_timeline_excludes_posts_from_unfollowed_users(
    other_user, book_in_db, db_session, access_token
):
    book_rating = BookRating(
        user_id=other_user.id,
        book_id=book_in_db.id,
        recommendation_score=5,
    )
    db_session.add(book_rating)
    db_session.commit()
    db_session.refresh(book_rating)

    public_post = ReadingPost(
        user_id=book_rating.user_id,
        book_id=book_rating.book_id,
        recommendation_score=book_rating.recommendation_score,
        recommendation_reason="フォローしていないユーザーの公開投稿",
        is_public=True,
    )
    db_session.add(public_post)
    db_session.commit()

    try:
        response = client.get(
            "/timeline/following",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        assert response.json() == []
    finally:
        db_session.delete(public_post)
        db_session.flush()
        db_session.delete(book_rating)
        db_session.commit()


def test_following_timeline_requires_authentication():
    response = client.get("/timeline/following")

    assert response.status_code == 401


def test_following_timeline_orders_posts_by_newest(
    registered_user,
    other_user,
    third_user,
    book_in_db,
    db_session,
    access_token,
):
    older_follow = Follow(
        follower_id=registered_user.id,
        followed_id=other_user.id,
    )
    newer_follow = Follow(
        follower_id=registered_user.id,
        followed_id=third_user.id,
    )
    older_book_rating = BookRating(
        user_id=other_user.id,
        book_id=book_in_db.id,
        recommendation_score=4,
    )
    newer_book_rating = BookRating(
        user_id=third_user.id,
        book_id=book_in_db.id,
        recommendation_score=5,
    )
    db_session.add_all(
        [older_follow, newer_follow, older_book_rating, newer_book_rating]
    )
    db_session.commit()
    db_session.refresh(older_book_rating)
    db_session.refresh(newer_book_rating)

    older_post = ReadingPost(
        user_id=older_book_rating.user_id,
        book_id=older_book_rating.book_id,
        recommendation_score=older_book_rating.recommendation_score,
        recommendation_reason="フォロー先の古い公開投稿",
        is_public=True,
        created_at=datetime(2026, 9, 25, tzinfo=timezone.utc),
    )
    newer_post = ReadingPost(
        user_id=newer_book_rating.user_id,
        book_id=newer_book_rating.book_id,
        recommendation_score=newer_book_rating.recommendation_score,
        recommendation_reason="フォロー先の新しい公開投稿",
        is_public=True,
        created_at=datetime(2026, 9, 26, tzinfo=timezone.utc),
    )
    db_session.add_all([older_post, newer_post])
    db_session.commit()
    db_session.refresh(older_post)
    db_session.refresh(newer_post)

    try:
        response = client.get(
            "/timeline/following",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        assert [post["reading_post_id"] for post in response.json()] == [
            newer_post.id,
            older_post.id,
        ]
    finally:
        db_session.delete(newer_post)
        db_session.delete(older_post)
        db_session.flush()
        db_session.delete(newer_book_rating)
        db_session.delete(older_book_rating)
        db_session.delete(newer_follow)
        db_session.delete(older_follow)
        db_session.commit()
