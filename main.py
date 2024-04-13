import os
from utils import *
import shutil


def copy_initial_files(full_path, lang):
    initial_files_path = getAbsPath(f"langs/{lang}")
    for root, dirs, files in os.walk(initial_files_path):
        for file in files:
            src_path = os.path.join(root, file)
            dst_path = os.path.join(
                full_path, os.path.relpath(src_path, initial_files_path)
            )
            if os.path.exists(dst_path):
                continue  # don't overwrite if file already exists
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)


def edit_pyproject_toml(full_path, repo_name):
    pyproject_toml_path = os.path.join(full_path, "pyproject.toml")
    if os.path.exists(pyproject_toml_path):
        with open(pyproject_toml_path, "r") as file:
            content = file.read()
        content = content.replace("placeholder-name", repo_name)
        with open(pyproject_toml_path, "w") as file:
            file.write(content)


def create_repository(repoPath):
    dev_folder_path = getConfig()["dev_folder_path"]
    full_path = os.path.join(dev_folder_path, repoPath)
    repo_name = repoPath.split("/")[-1]
    os.makedirs(full_path, exist_ok=True)
    run_command(f"cd {full_path}; git init")
    return full_path, repo_name


def initialize_repository(full_path, lang, repo_name):
    copy_initial_files(full_path, lang)

    config = getConfig()
    if lang in config["initCommands"]:
        for command in config["initCommands"][lang]:
            run_command(f"cd {full_path}; {command}")

    edit_pyproject_toml(full_path, repo_name)


def open_code_editor(full_path):
    run_command(f"code '{full_path}'")
    run_command(f"code '{full_path}/src/main.*'")


def create_github_repository(full_path, repo_name):
    stdout = run_command(f"cd {full_path}; git remote -v")[0]
    if not stdout.strip():
        run_command(f"cd {full_path} && git add . && git commit -m 'Initial commit'")
        run_command(
            f"cd {full_path}; gh repo create {repo_name} --private --source=. --remote=origin"
        )
        run_command(f"cd {full_path}; git push --set-upstream origin master")


def main():
    args = parse_arguments()
    if not validate_arguments(args):
        return

    full_path, repo_name = create_repository(args.repoPath)
    initialize_repository(full_path, args.lang, repo_name)
    open_code_editor(full_path)
    create_github_repository(full_path, repo_name)


if __name__ == "__main__":
    main()
