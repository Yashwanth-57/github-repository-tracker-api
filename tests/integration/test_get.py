
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.repository import Repository

from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
async def test_get_repository_success():

    repo_id = None

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

        response = await client.get(
            f"/repositories/{repo_id}"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["github_id"] == 123
    assert data["name"] == "react"
    assert data["owner"] == "facebook"


@pytest.mark.asyncio
async def test_get_repository_not_found():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        response = await client.get(
            "/repositories/999999"
        )

    assert response.status_code == 404
