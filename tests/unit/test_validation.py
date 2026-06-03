
import pytest
from pydantic import ValidationError

from app.schemas.repository import RepositoryCreate


# VALID URL

def test_valid_github_url():

    data = RepositoryCreate(
        url="https://github.com/octocat/Hello-World"
    )

    assert str(data.url) == (
        "https://github.com/octocat/Hello-World"
    )


# WRONG DOMAIN

def test_invalid_domain():

    with pytest.raises(ValidationError):

        RepositoryCreate(
            url="https://gitlab.com/test/repo"
        )


# MALFORMED URL

def test_invalid_url_format():

    with pytest.raises(ValidationError):

        RepositoryCreate(
            url="not-a-valid-url"
        )


# MISSING FIELD

def test_missing_url():

    with pytest.raises(ValidationError):

        RepositoryCreate()

