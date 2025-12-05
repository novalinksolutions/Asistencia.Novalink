import os
import sys
from pathlib import Path
import base64
import logging
from operator import itemgetter
from dotenv import load_dotenv
from github import Github, InputGitTreeElement, Auth

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("GitHubSync")


def load_environment():
    """Load environment variables from .env file."""
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logger.info("✓ Loaded .env file")
    else:
        logger.warning("! No .env file found in current directory")


def get_github_client():
    """Initialize GitHub client using the modern Auth method."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.error("✗ GITHUB_TOKEN not found in environment variables")
        print("Please ensure GITHUB_TOKEN is set in your .env file or environment.")
        sys.exit(1)
    try:
        auth = Auth.Token(token)
        g = Github(auth=auth)
        user = g.get_user()
        logger.info(f"✓ Authenticated as GitHub user: {user.login}")
        return g
    except Exception as e:
        logging.exception(f"✗ Authentication failed: {e}")
        sys.exit(1)


def should_exclude(path_obj: Path) -> bool:
    """
    Determine if a file or directory should be excluded from sync.
    path_obj: A Path object relative to the project root.
    """
    EXCLUDE_NAMES = {
        ".git",
        "__pycache__",
        ".reflex",
        ".web",
        "node_modules",
        "venv",
        ".env",
        ".venv",
        ".DS_Store",
        ".pytest_cache",
        "dist",
        "build",
        "coverage",
        ".vscode",
        ".idea",
    }
    EXCLUDE_EXTENSIONS = {".pyc", ".pyo", ".pyd", ".so", ".dll"}
    for part in path_obj.parts:
        if part in EXCLUDE_NAMES:
            return True
    if path_obj.suffix in EXCLUDE_EXTENSIONS:
        return True
    if path_obj.name == "rxconfig.pyc":
        return True
    return False


def collect_files(base_dir: Path):
    """Walk directory and collect all valid files for sync."""
    file_list = []
    logger.info(f"Scanning files in {base_dir}...")
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [
            d for d in dirs if not should_exclude(Path(root).relative_to(base_dir) / d)
        ]
        for file in files:
            file_path = Path(root) / file
            try:
                relative_path = file_path.relative_to(base_dir)
                if not should_exclude(relative_path):
                    posix_path = str(relative_path).replace("\\", "/")
                    file_list.append((posix_path, file_path))
            except ValueError as e:
                logging.exception(f"Error processing file path: {e}")
                continue
    return sorted(file_list, key=itemgetter(0))


def sync_to_github():
    """Main execution flow."""
    print("""
--- Novalink Project GitHub Synchronizer ---
""")
    load_environment()
    g = get_github_client()
    repo_name = "novalinksolutions/Asistencia.Novalink"
    try:
        repo = g.get_repo(repo_name)
        logger.info(f"✓ Target Repository: {repo.full_name}")
    except Exception as e:
        logging.exception(
            f"✗ Could not access repository {repo_name}. Check permissions."
        )
        sys.exit(1)
    base_dir = Path.cwd()
    files_to_upload = collect_files(base_dir)
    total_files = len(files_to_upload)
    if total_files == 0:
        logger.warning(
            "No files found to upload. Check your exclude patterns or directory."
        )
        return
    logger.info(f"✓ Found {total_files} files to synchronize")
    try:
        main_branch = repo.get_branch("main")
        latest_commit = main_branch.commit
        base_tree_sha = latest_commit.commit.tree.sha
        logger.info(f"✓ Base Commit SHA: {latest_commit.sha[:8]}")
    except Exception as e:
        logging.exception(f"✗ Failed to fetch main branch info: {e}")
        sys.exit(1)
    tree_elements = []
    logger.info("🚀 Processing files and creating Git blobs...")
    processed_count = 0
    errors = []
    print(f"[{'=' * 30}] 0%")
    for i, (git_path, local_path) in enumerate(files_to_upload, 1):
        try:
            with open(local_path, "rb") as f:
                content = f.read()
            blob = repo.create_git_blob(
                base64.b64encode(content).decode("utf-8"), "base64"
            )
            element = InputGitTreeElement(
                path=git_path, mode="100644", type="blob", sha=blob.sha
            )
            tree_elements.append(element)
            processed_count += 1
            if i % 10 == 0 or i == total_files:
                percent = int(i / total_files * 30)
                bar = "=" * percent + " " * (30 - percent)
                percentage = int(i / total_files * 100)
                print(f"\r[{bar}] {percentage}% ({i}/{total_files})", end="")
        except Exception as e:
            logging.exception(f"Failed to process {git_path}: {e}")
            error_msg = f"Failed to process {git_path}: {e}"
            errors.append(error_msg)
    print("")
    if errors:
        logger.warning(f"⚠️ Encountered {len(errors)} errors during file processing.")
        for err in errors[:5]:
            logger.warning(f"  - {err}")
        if len(errors) > 5:
            logger.warning(f"  ... and {len(errors) - 5} more.")
    if not tree_elements:
        logger.error("✗ No valid tree elements created. Aborting sync.")
        sys.exit(1)
    try:
        logger.info("🌳 Creating Git Tree...")
        base_tree = repo.get_git_tree(base_tree_sha)
        new_tree = repo.create_git_tree(tree_elements, base_tree)
        logger.info("📝 Creating Commit...")
        parent_commit = repo.get_git_commit(latest_commit.sha)
        commit_message = f"Sync: Automated update ({processed_count} files)"
        new_commit = repo.create_git_commit(commit_message, new_tree, [parent_commit])
        logger.info("🚀 Updating refs/heads/main...")
        ref = repo.get_git_ref("heads/main")
        ref.edit(new_commit.sha)
        print(
            """
"""
            + "=" * 50
        )
        logger.info("✅ SYNCHRONIZATION SUCCESSFUL")
        print(f"Commit SHA: {new_commit.sha}")
        print(f"View on GitHub: https://github.com/{repo_name}/commit/{new_commit.sha}")
        print(
            "=" * 50
            + """
"""
        )
    except Exception as e:
        logging.exception(f"✗ Critical error during GitHub push: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sync_to_github()