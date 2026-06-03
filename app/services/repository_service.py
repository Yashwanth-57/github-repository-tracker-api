from sqlalchemy import select
from app.models.repository import Repository
from app.services.github_service import fetch_github_repo
from app.core.exceptions import NotFoundError, ConflictError


async def create_repository_service(url: str, session):

    repo_data = await fetch_github_repo(url)

    if repo_data is None:
        raise NotFoundError()

    existing = await session.execute(
            select(Repository).where(
                Repository.github_id == repo_data["github_id"]
            )
        )

    if existing.scalar_one_or_none():
            raise ConflictError()

    repo = Repository(**repo_data)

    session.add(repo)
   
    await session.flush()

    return repo


async def get_repo_service(repo_id: int, session):
    result = await session.execute(
        select(Repository).where(Repository.id == repo_id)
    )

    repo = result.scalar_one_or_none()

    if not repo:
        raise NotFoundError()
    
    return repo


async def delete_repo_service(repo_id: int, session):

    result = await session.execute(
        select(Repository).where(Repository.id == repo_id)
    )

    repo = result.scalar_one_or_none()

    if not repo:
        raise NotFoundError()

    await session.delete(repo)
    


    return True

async def refresh_repo_service(repo_id: int, session):

    result = await session.execute(
        select(Repository).where(Repository.id == repo_id)
    )

    repo = result.scalar_one_or_none()

    if not repo:
        raise NotFoundError()

    repo_data = await fetch_github_repo(repo.repo_url)

    if repo_data is None:
        raise NotFoundError()

    repo.name = repo_data["name"]
    repo.description = repo_data["description"]
    repo.language = repo_data["language"]
    repo.stars = repo_data["stars"]

    
    await session.flush()

    return repo