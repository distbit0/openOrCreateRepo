import subprocess
import sys
import os

dev_folder_path = "/home/pimania/Dev/"


def run_command(command):
    print(f"Executing: {command}")
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    print(stdout.decode("utf-8"), stderr.decode("utf-8"))
    return stdout, stderr


def main():
    if len(sys.argv) < 2:
        print(
            "Missing repository name. Usage: python script.py nameOfRepo or parentFolder/nameOfRepo"
        )

    # Create parent folder if necessary
    full_path = os.path.join(dev_folder_path, sys.argv[1])
    repo_name = sys.argv[1].split("/")[-1]
    os.makedirs(full_path, exist_ok=True)

    # Initialize git repository
    run_command(f"cd {full_path}; git init .")

    if len([name for name in os.listdir(full_path) if name != ".git"]) == 0:
        run_command(f"touch {full_path}/main.py")

    # Make the first commit
    run_command(f"cd {full_path} && git add . && git commit -m 'Initial commit'")

    # Check if a remote repository exists
    stdout = run_command(f"cd {full_path}; git remote -v")[0]

    # Create GitHub repository and set as default push destination only if no remote repo exists
    if not stdout.strip():
        run_command(
            f"cd {full_path}; gh repo create {repo_name} --private --source=. --remote=origin"
        )

    run_command(f"cd {full_path}; git push --set-upstream origin master")

    # Open folder in VSCode
    run_command(f"code {full_path}")


if __name__ == "__main__":
    main()
