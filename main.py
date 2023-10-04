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
    return stdout.decode("utf-8"), stderr.decode("utf-8")


def main():
    if len(sys.argv) < 2:
        print(
            "Missing repository name. Usage: python script.py nameOfRepo or parentFolder/nameOfRepo"
        )
        # sys.exit(1)

    repo_name = sys.argv[1].split("/")[1] if "/" in sys.argv[1] else sys.argv[1]

    # Create parent folder if necessary
    full_path = os.path.join(dev_folder_path, repo_name)
    os.makedirs(full_path, exist_ok=True)

    # Initialize git repository
    stdout, stderr = run_command(f"cd {full_path}; git init .")
    if stderr.lower():
        print(f"Error initializing git: {stderr}")
        # sys.exit(1)

    # Create main.py
    stdout, stderr = run_command(f"touch {full_path}/main.py")
    if stderr.lower():
        print(f"Error creating main.py: {stderr}")
        # sys.exit(1)

    # Make the first commit
    stdout, stderr = run_command(
        f"cd {full_path} && git add . && git commit -m 'Initial commit'"
    )
    if stderr.lower():
        print(f"Error making the first commit: {stderr}")
        # sys.exit(1)

    # Create GitHub repository and set as default push destination
    stdout, stderr = run_command(
        f"cd {full_path}; gh repo create {repo_name} --confirm --private --push --source ."
    )
    if stderr.lower():
        print(f"Error creating GitHub repo: {stderr}")
        # sys.exit(1)

    # Open folder in VSCode
    stdout, stderr = run_command(f"code {full_path}")
    if stderr.lower():
        print(f"Error opening in VSCode: {stderr}")
        # sys.exit(1)


if __name__ == "__main__":
    main()
