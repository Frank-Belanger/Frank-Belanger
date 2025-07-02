import time
import requests
import json
import pathlib
import re
import os

root = pathlib.Path(__file__).parent.resolve()
TOKEN = os.environ.get("GITHUB_TOKEN", "")

def replace_chunk(content, marker, chunk):
    r = re.compile(
        "<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    chunk = "<!-- {} starts -->\n{}\n<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)

if __name__ == "__main__":
    readme = root / "README.md"
    endpoint = "https://api.github.com/users/Frank-Belanger/repos"
    headers = {"Authorization": "Bearer {}".format(TOKEN)}
    fetched = requests.get(endpoint, headers=headers).json()
    print(fetched)
    tableFirstPart = "| Name | Last Update | Description |\n"
    tableScndPart = "|------|-------------|-------------|\n"
    table = tableFirstPart + tableScndPart
    repos = "\n".join(
        [
            "| [{name}]({url}) | {updatedAt} | "
            .format(
                name=repo["name"],
                url=repo["html_url"],
                updatedAt=repo["updated_at"].split("T")[0]
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
    os.environ["TZ"] = "America/New_York"
    time.tzset()
    timestamp = "This <i>README</i> was last updated {}".format(time.strftime("%A %d of %b %Y, at %H:%M EST"))
    rewritten = replace_chunk(rewritten, "timestamp", timestamp)
    readme.open("w").write(rewritten)
