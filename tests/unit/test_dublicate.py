

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.repository_service import (
    create_repository_service
)

from app.core.exceptions import ConflictError


@pytest.mark.asyncio
async def test_duplicate_repository():

    # MOCK DATABASE SESSION
    session = AsyncMock()

    # MOCK EXISTING QUERY RESULT
    result = MagicMock()
    result.scalar_one_or_none.return_value = True

    session.execute.return_value = result

    # MOCK EXTERNAL API RESPONSE
    # IMPORTANT:
    # Patch fetch_github_repo if needed depending on your structure

    from unittest.mock import patch

    mocked_repo = {
        "github_id": 123,
        "name": "Hello-World",
        "owner": "octocat",
        "description": "Test Repo",
        "language": "Python",
        "stars": 100,
        "repo_url": "https://github.com/octocat/Hello-World"
    }

    with patch(
        "app.services.repository_service.fetch_github_repo",
        return_value=mocked_repo
    ):

        with pytest.raises(ConflictError):

            await create_repository_service(
                "https://github.com/octocat/Hello-World",
                session
            )
