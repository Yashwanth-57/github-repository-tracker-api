import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.repository import Repository

from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
async def test_delete_repository_success():

    async with TestingSessionLocal() as session:

        repo = Repository(
            github_id=999,
            name="vue",
            owner="evan",
            description="frontend framework",
            language="JavaScript",
            stars=500,
            repo_url="https://github.com/vuejs/vue"
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

        response = await client.delete(
            f"/repositories/{repo_id}"
        )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_repository_not_found():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        response = await client.delete(
            "/repositories/999999"
        )

    assert response.status_code == 404