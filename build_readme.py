from python_graphql_client import GraphqlClient
import json
import pathlib
import re
import os

root = pathlib.Path(__file__).parent.resolve()
client = GraphqlClient(endpoint="https://api.github.com/graphql")

TOKEN = os.environ.get("GITHUB_TOKEN", "")

def replace_chunk(content, marker, chunk):
    r = re.compile(
        "<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    chunk = "<!-- {} starts -->\n{}\n<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)

def make_query():
    return """
{
  viewer {
    repositories(last: 3) {
      nodes {
        name
        url
        updatedAt
        description
      }
    }
  }
}
"""

def fetch_repos(oauth_token):
    repos = []
    data = client.execute(
        query=make_query(),
        headers={"Authorization": "Bearer {}".format(oauth_token)},
    )
    #print()
    #print(json.dumps(data, indent=4))
    #print()
    for repo in data["data"]["viewer"]["repositories"]["nodes"]:
        repos.append(
            {
                'name': repo["name"],
                'url': repo["url"],
                'description': repo["description"],
                'updatedAt': repo["updatedAt"].split("T")[0]
            }
        )

    return repos

if __name__ == "__main__":
    readme = root / "README.md"
    fetched = fetch_repos(TOKEN)
    tableFirstPart = "| Name | Last Update | Description |\n"
    tableScndPart = "|------|-------------|-------------|\n"
    table = tableFirstPart + tableScndPart
    repos = "\n".join(
        [
            "| [{name}]({url}) | {updatedAt} | "
            .format(
                name=repo["name"],
                url=repo["url"],
                updatedAt=repo["updatedAt"]
            )
            + "{description} | ".format(
                description=repo["description"]
            )
            for repo in fetched
        ]
    )
    chunk = table + repos
    readme_contents = readme.open().read()
    rewritten = replace_chunk(readme_contents, "latest_repos", chunk)
    readme.open("w").write(rewritten)