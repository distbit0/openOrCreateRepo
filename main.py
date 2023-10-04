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


def open_subfolder(base_dir, pattern):
    # Convert pattern to lowercase for case-insensitive search
    pattern = pattern.lower()
    pattern = "*" + pattern + "*"
    pattern = pattern.replace("/", "*/*")

    matching_folders = []

    for root, dirs, _ in os.walk(base_dir):
        for dir in dirs:
            # Build the relative path from base_dir to the directory
            rel_path = os.path.relpath(os.path.join(root, dir), base_dir)

            # Convert to lowercase for case-insensitive comparison
            lower_rel_path = rel_path.lower()

            # Use fnmatch to find directories that match the pattern
            sameDepth = pattern.count("/") == lower_rel_path.count("/")
            if fnmatch.fnmatch(lower_rel_path, pattern) and sameDepth:
                full_path = os.path.join(root, dir)
                matching_folders.append(full_path)

    if len(matching_folders) == 1:
        run_command(f"code {matching_folders[0]}")
        print(f"Opened folder: {matching_folders[0]}")
    elif matching_folders:
        print("Multiple matching folders found:\n")
        for i, folder in enumerate(matching_folders):
            print("\t" + str(i + 1) + "  " + folder.replace(dev_folder_path, ""))
        selectedFolder = int(input("\n\tSelect folder: ")) - 1
        print(f"Opened folder: {matching_folders[selectedFolder]}")
        run_command(f"code {matching_folders[selectedFolder]}")
    else:
        print("No matching folder found.")


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
        if args.repoPath:
            open_subfolder(dev_folder_path, args.repoPath)
        else:
            print("Error: -o flag requires a repoPath.")
        return

    if args.repoPath:
        repoPath = args.repoPath
        # Your existing code to handle repoPath
    else:
        print(
            "Missing repository name. Usage: python script.py nameOfRepo or parentFolder/nameOfRepo"
        )

    # Create parent folder if necessary
    full_path = os.path.join(dev_folder_path, repoPath)
    repo_name = repoPath.split("/")[-1]
    os.makedirs(full_path, exist_ok=True)

    # Initialize git repository
    run_command(f"cd {full_path}; git init")

    if len([name for name in os.listdir(full_path) if name != ".git"]) == 0:
        run_command(f"touch {full_path}/main.py")

    run_command(f"code {full_path}")

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
