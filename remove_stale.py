from argparse import ArgumentParser
from github import Github, GithubException, PullRequest
import subprocess
from pathlib import Path
import shutil


parser = ArgumentParser()
parser.add_argument("gh_token")
parser.add_argument("repository")


def main() -> None:
    args = parser.parse_args()
    github = Github(login_or_token=args.gh_token)
    repo = github.get_repo(args.repository)

    subprocess.run(["git", "checkout", "gh-pages"], check=True)

    count_deleted = 0

    for path in Path.cwd().iterdir():
        if not path.is_dir():
            continue

        if not path.name.isdigit():
            continue

        try:
            pr = repo.get_pull(int(path.name))
            if pr.state == "open":
                continue
        except GithubException:
            pass

        count_deleted += 1
        shutil.rmtree(path)

    if count_deleted:
        subprocess.run(
            ["git", "commit", "-a", "-m", f"delete {count_deleted} stale previews"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)

    subprocess.run(["git", "checkout", "-"], check=True)


if __name__ == "__main__":
    main()
