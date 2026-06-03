import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch

from app.main import app


mock_repo_data = {
    "github_id": 123,
    "name": "react",
    "owner": "facebook",
    "description": "frontend library",
    "language": "JavaScript",
    "stars": 100,
    "repo_url": "https://github.com/facebook/react"
}


@pytest.mark.asyncio
@patch("app.services.repository_service.fetch_github_repo")
async def test_post_repository_success(mock_fetch):

    mock_fetch.return_value = mock_repo_data

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        response = await client.post(
            "/repositories",
            json={"url": "https://github.com/facebook/react"}
        )

    assert response.status_code == 201

    data = response.json()
    assert data["github_id"] == 123
    assert data["name"] == "react"
    assert data["owner"] == "facebook"