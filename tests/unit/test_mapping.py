
# from app.utils.mappers import map_github_response



# def test_github_response_mapping():

#     raw_response = {
#         "id": 123456,
#         "name": "Hello-World",
#         "owner": {
#             "login": "octocat"
#         },
#         "description": "Testing repository",
#         "language": "Python",
#         "stargazers_count": 500,
#         "html_url": "https://github.com/octocat/Hello-World"
#     }

#     mapped = map_github_response(raw_response)

#     assert mapped["github_id"] == 123456
#     assert mapped["name"] == "Hello-World"
#     assert mapped["owner"] == "octocat"
#     assert mapped["description"] == "Testing repository"
#     assert mapped["language"] == "Python"
#     assert mapped["stars"] == 500
#     assert mapped["repo_url"] == (
#         "https://github.com/octocat/Hello-World"
#     )

