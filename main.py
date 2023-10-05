import subprocess
import os
import json
from os import path
import fnmatch
import argparse
import glob


def getConfig():
    configFileName = getAbsPath("config.json")
    with open(configFileName) as config:
        config = json.loads(config.read())

    return config


def getAbsPath(relPath):
    basepath = path.dirname(__file__)
    fullPath = path.abspath(path.join(basepath, relPath))

    return fullPath


dev_folder_path = getConfig()["dev_folder_path"]


def run_command(command):
    print(f"Executing: {command}")
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    print(stdout.decode("utf-8"), stderr.decode("utf-8"))
    return stdout, stderr


def main():
    parser = argparse.ArgumentParser(description="Script for repository management.")
    parser.add_argument(
        "repoPath",
        type=str,
        nargs="?",
        help="Path for the repository, either nameOfRepo or parentFolder/nameOfRepo",
    )

    args = parser.parse_args()

    if args.repoPath:
        repoPath = args.repoPath
    else:
        print(
            "Missing repository name. Usage: python main.py nameOfRepo or parentFolder/nameOfRepo"
        )
        return

    # Create parent folder if necessary
    full_path = os.path.join(dev_folder_path, repoPath)
    repo_name = repoPath.split("/")[-1]
    os.makedirs(full_path, exist_ok=True)

    # Initialize git repository
    run_command(f"cd {full_path}; git init")

    if len([name for name in os.listdir(full_path) if name != ".git"]) == 0:
        run_command(f"touch {full_path}/" + getConfig()["firstFileName"])

    run_command(f"code '{full_path}'")

    # Check if a remote repository exists
    stdout = run_command(f"cd {full_path}; git remote -v")[0]

    # Create GitHub repository and set as default push destination only if no remote repo exists
    if not stdout.strip():
        run_command(f"cd {full_path} && git add . && git commit -m 'Initial commit'")
        run_command(
            f"cd {full_path}; gh repo create {repo_name} --private --source=. --remote=origin"
        )
        run_command(f"cd {full_path}; git push --set-upstream origin master")


if __name__ == "__main__":
    main()
