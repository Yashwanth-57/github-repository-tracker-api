from fastapi import APIRouter
from app.database.db import AsyncSessionLocal
from app.schemas.repository import RepositoryCreate, RepositoryResponse
from app.database.db import get_session

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.services.repository_service import (
    create_repository_service,
    get_repo_service,
    delete_repo_service,
    refresh_repo_service
)

from app.core.exceptions import NotFoundError
# from app.core.sucess import success_response

router = APIRouter()


# POST
@router.post("/repositories", response_model=RepositoryResponse, status_code=201)
async def create_repository(data: RepositoryCreate, session: AsyncSession = Depends(get_session)):
    # async with AsyncSessionLocal() as session:
        try:
            repo = await create_repository_service(str(data.url), session)
            await session.commit()
            return repo

        except Exception:
            await session.rollback()
            raise
    


# GET
@router.get("/repositories/{id}", response_model=RepositoryResponse)
async def get_repository(id: int, session: AsyncSession = Depends(get_session)):

    # async with AsyncSessionLocal() as session:
        try:

            repo = await get_repo_service(id, session)

            if not repo:
                raise NotFoundError()
    
            return repo
        except Exception:
            await session.rollback()
            raise


# DELETE
@router.delete("/repositories/{id}", status_code=204)
async def delete_repository(id: int, session: AsyncSession = Depends(get_session)):

    # async with AsyncSessionLocal() as session:
        try:

            deleted = await delete_repo_service(id, session)

            await session.commit()
            
            return 
        except Exception:

            await session.rollback()
            raise


# PUT
@router.put("/repositories/{id}", response_model=RepositoryResponse)
async def refresh_repository(id: int, session: AsyncSession = Depends(get_session)):

    # async with AsyncSessionLocal() as session:
        try:
            result = await refresh_repo_service(id, session)
    
            await session.commit()


            if result is None or result == "deleted":
                raise NotFoundError()
    
            return result
        except Exception:
            await session.rollback()
            raise
    