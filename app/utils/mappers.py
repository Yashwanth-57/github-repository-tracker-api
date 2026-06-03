
def map_github_response(data):

    return {
        "github_id": data["id"],
        "name": data["name"],
        "owner": data["owner"]["login"],
        "description": data.get("description"),
        "language": data.get("language"),
        "stars": data["stargazers_count"],
        "repo_url": data["html_url"]
    }