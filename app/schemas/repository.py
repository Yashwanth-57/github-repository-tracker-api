from pydantic import BaseModel, HttpUrl, field_validator, ConfigDict
from datetime import datetime

class RepositoryCreate(BaseModel):
    url: HttpUrl

    @field_validator("url")
    @classmethod
    def validate_github_url(cls, v):
        if "github.com" not in str(v):
            raise ValueError("Only GitHub URLs allowed")
        
        url = str(v)

        if "github.com" not in url:
            raise ValueError("Only GitHub URLs allowed")

        parts = url.replace(
            "https://github.com/", ""
        ).split("/")

        if len(parts) < 2:
            raise ValueError(
                "Repository URL must contain owner and repository name"
            )
        return v

class RepositoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    github_id: int
    name: str
    owner: str
    description: str | None = None
    language: str | None = None
    stars: int
    repo_url: str
    created_at: datetime
    updated_at: datetime
    