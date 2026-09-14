from urllib.parse import urlparse


def is_valid_git_url(repo_url: str) -> bool:
    parsed = urlparse(repo_url)

    if parsed.scheme != "https":
        return False

    if parsed.netloc != "github.com":
        return False

    parts = parsed.path.strip("/").split("/")

    if len(parts) != 2:
        return False

    return True