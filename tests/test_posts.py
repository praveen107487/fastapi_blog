import pytest
from httpx import AsyncClient
from tests.conftest import auth_header, create_test_user, login_user

# ==========================================
#               GET ALL POSTS
# ==========================================

@pytest.mark.anyio
async def test_get_posts_empty(client: AsyncClient):
    response = await client.get("/api/posts")

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["limit"] == 5
    assert data["offset"] == 0


@pytest.mark.anyio
async def test_get_post_not_found(client: AsyncClient):
    response = await client.get("/api/posts/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


# ==========================================
#               CREATE POSTS
# ==========================================

@pytest.mark.anyio
async def test_create_post_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.post(
        "/api/posts",
        json={
            "title": "My First Post", 
            "content": "This is the content",
            "user_id": user["id"]
        },
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My First Post"
    assert data["content"] == "This is the content"
    assert data["user_id"] == user["id"]
    assert "id" in data
    assert "date_posted" in data
    assert data["author"]["username"] == "testuser"


@pytest.mark.anyio
async def test_create_post_unauthorized(client: AsyncClient):
    response = await client.post(
        "/api/posts",
        json={
            "title": "Test Post", 
            "content": "Test content",
            "user_id": 1
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# ==========================================
#               UPDATE POSTS
# ==========================================

@pytest.mark.anyio
async def test_update_post_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.post(
        "/api/posts",
        json={
            "title": "Original Title", 
            "content": "Original content",
            "user_id": user["id"]
        },
        headers=headers,
    )
    assert response.status_code == 201
    post_id = response.json()["id"]

    response = await client.patch(
        f"/api/posts/{post_id}",
        json={"title": "Updated Title"},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Original content"


@pytest.mark.anyio
async def test_update_post_wrong_user(client: AsyncClient):
    user1 = await create_test_user(client, username="user1", email="user1@example.com")
    token1 = await login_user(client, email="user1@example.com")

    response = await client.post(
        "/api/posts",
        json={
            "title": "User 1's Post", 
            "content": "Only user 1 can edit this",
            "user_id": user1["id"]
        },
        headers=auth_header(token1),
    )
    assert response.status_code == 201
    post_id = response.json()["id"]

    await create_test_user(client, username="user2", email="user2@example.com")
    token2 = await login_user(client, email="user2@example.com")

    response = await client.patch(
        f"/api/posts/{post_id}",
        json={"title": "Hacked Title"},
        headers=auth_header(token2),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to edit this post."


# ==========================================
#               PAGINATION
# ==========================================

@pytest.mark.anyio
async def test_get_posts_with_pagination(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    for i in range(5):
        response = await client.post(
            "/api/posts",
            json={
                "title": f"Post {i}", 
                "content": f"Content for post {i}",
                "user_id": user["id"]
            },
            headers=headers,
        )
        assert response.status_code == 201

    response = await client.get("/api/posts")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5
    assert data["limit"] == 5
    assert data["offset"] == 0

    response = await client.get("/api/posts?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["limit"] == 2

    response = await client.get("/api/posts?offset=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["offset"] == 2
    assert data["limit"] == 2