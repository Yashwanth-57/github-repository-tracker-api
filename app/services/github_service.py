import httpx
from app.core.exceptions import ExternalAPIError, ExternalAPITimeoutError
from app.utils.mappers import map_github_response
from app.core.config import settings



def extract_repo(url: str):
    parts = url.replace("https://github.com/", "").split("/")
    print("legth of partsss", len(parts))
    return parts[0], parts[1]


async def fetch_github_repo(url: str):

    owner, repo = extract_repo(url)
    api_url = (
    f"{settings.GITHUB_API_BASE_URL}"
    f"/repos/{owner}/{repo}"
)

    try:
        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
            response = await client.get(api_url)
            print("resposnssssssssssss", response)

    except httpx.TimeoutException:
        raise ExternalAPITimeoutError()

    except httpx.RequestError:
        raise ExternalAPIError()

    if response.status_code == 404:
        return None

    if response.status_code != 200:
        raise ExternalAPIError()

    data = response.json()

    print("dataaaaaa", data);

    return map_github_response(data)