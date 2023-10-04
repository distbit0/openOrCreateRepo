import subprocess
import os
import json
from os import path
import fnmatch
import argparse


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


def open_subfolder(base_dir, pattern, additionalPatterns=[]):
    # Convert pattern to lowercase for case-insensitive search
    patterns = list(additionalPatterns)
    patterns.append("*" + pattern.replace("/", "*/*").lower() + "*")
    maxPatternDepth = max([pattern.count("/") for pattern in patterns])

    maxDepth = min(getConfig()["maxDepth"], maxPatternDepth)
    matching_folders = []
    for root, dirs, _ in os.walk(base_dir):
        current_depth = root[len(base_dir) - 1 :].rstrip(os.sep).count(os.sep)

        if current_depth > maxDepth:
            continue

        for dir in dirs:
            # Build the relative path from base_dir to the directory
            currentDirPath = os.path.join(root, dir)
            rel_path = os.path.relpath(currentDirPath, base_dir).lower()

            matches = True
            # Use fnmatch to find directories that match the pattern
            for pattern in patterns:
                if not fnmatch.fnmatch(rel_path, pattern):
                    matches = False
                    break

            if matches:
                matching_folders.append(currentDirPath)

    if len(matching_folders) == 1:
        run_command(f"code '{matching_folders[0]}'")
    else:
        if len(matching_folders) == 0:
            print("No matching folders found.")
        else:
            print("\nMultiple matching folders found:\n")
        for i, folder in enumerate(matching_folders):
            print("\t" + str(i + 1) + "  " + folder.replace(dev_folder_path, ""))
        filter = input("\n\tFilter: ")
        if filter in [str(i + 1) for i in range(len(matching_folders))]:
            selectedFolder = int(filter) - 1
            run_command(f"code '{matching_folders[selectedFolder]}'")
        else:
            open_subfolder(base_dir, filter, patterns)


def main():
    parser = argparse.ArgumentParser(description="Script for repository management.")
    parser.add_argument(
        "repoPath",
        type=str,
        nargs="?",
        help="Path for the repository, either nameOfRepo or parentFolder/nameOfRepo",
    )
    parser.add_argument(
        "-o",
        "--open",
        action="store_true",
        help="Open the subfolder specified by repoPath",
    )

    args = parser.parse_args()

    if args.open:
        repoPath = args.repoPath if args.repoPath else ""
        open_subfolder(dev_folder_path, repoPath)
        return

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
