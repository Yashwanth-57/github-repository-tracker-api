import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch

from app.main import app
from app.models.repository import Repository

from tests.conftest import TestingSessionLocal


updated_repo_data = {
    "github_id": 123,
    "name": "react-updated",
    "owner": "facebook",
    "description": "updated description",
    "language": "TypeScript",
    "stars": 9999,
    "repo_url": "https://github.com/facebook/react"
}


@pytest.mark.asyncio
@patch("app.services.repository_service.fetch_github_repo")
async def test_put_repository_success(mock_fetch):

    mock_fetch.return_value = updated_repo_data

    async with TestingSessionLocal() as session:

        repo = Repository(
            github_id=123,
            name="react",
            owner="facebook",
            description="frontend library",
            language="JavaScript",
            stars=100,
            repo_url="https://github.com/facebook/react"
        )

        session.add(repo)

        await session.flush()

        repo_id = repo.id

        await session.commit()

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        response = await client.put(
            f"/repositories/{repo_id}"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "react-updated"
    assert data["description"] == "updated description"
    assert data["language"] == "TypeScript"
    assert data["stars"] == 9999


@pytest.mark.asyncio
@patch("app.services.repository_service.fetch_github_repo")
async def test_put_repository_not_found(mock_fetch):

    mock_fetch.return_value = updated_repo_data

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        response = await client.put(
            "/repositories/999999"
        )

    assert response.status_code == 404