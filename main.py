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
    ## get author string from git
    name = run_command("git config user.name")[0].strip().decode("utf-8")
    email = run_command("git config user.email")[0].strip().decode("utf-8")
    author = f"{name} <{email}>"
    pyproject_toml_path = os.path.join(full_path, "pyproject.toml")
    if os.path.exists(pyproject_toml_path):
        with open(pyproject_toml_path, "r") as file:
            content = file.read()
        content = content.replace("placeholder-project-name", repo_name)
        content = content.replace("placeholder-author", name)
        content = content.replace("placeholder@email.com", email)
        with open(pyproject_toml_path, "w") as file:
            file.write(content)


def create_repository(repoPath):
    dev_folder_path = getConfig()["dev_folder_path"]
    full_path = os.path.join(dev_folder_path, repoPath)
    repo_name = repoPath.split("/")[-1]
    os.makedirs(full_path, exist_ok=True)
    run_command(f"cd {full_path}; git init")
    return full_path, repo_name


def run_init_commands(full_path, lang, repo_name):
    edit_pyproject_toml(full_path, repo_name)
    config = getConfig()
    if lang in config["initCommands"]:
        for command in config["initCommands"][lang]:
            if command.startswith("poetry"):
                # Replace poetry commands with uv commands
                if command.startswith("poetry add"):
                    command = command.replace("poetry add", "uv add")
                elif command == "poetry install":
                    command = "uv sync"
            run_command(f"cd {full_path}; {command}")
    
    # Initialize uv project
    run_command(f"cd {full_path}; uv sync")


def open_code_editor(full_path, lang):
    run_command(f"code '{full_path}'")
    run_command(f"code '{full_path}/src/main.{lang}'")


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
    copy_initial_files(full_path, args.lang)
    open_code_editor(full_path, args.lang)
    run_init_commands(full_path, args.lang, repo_name)
    create_github_repository(full_path, repo_name)


if __name__ == "__main__":
    main()
