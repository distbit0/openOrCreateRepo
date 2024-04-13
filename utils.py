import subprocess
import json
from os import path
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


def parse_arguments():
    parser = argparse.ArgumentParser(description="Script for repository management.")
    parser.add_argument(
        "repoPath",
        type=str,
        nargs="?",
        help="Path for the repository, either nameOfRepo or parentFolder/nameOfRepo",
    )
    parser.add_argument(
        "-l",
        "--lang",
        type=str,
        default="py",
        help="Language of the repository (default: py)",
    )
    return parser.parse_args()


def validate_arguments(args):
    if not args.repoPath:
        print(
            "Missing repository name. Usage: python main.py nameOfRepo or parentFolder/nameOfRepo"
        )
        return False
    return True


def run_command(command):
    print(f"Executing: {command}")
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    print(stdout.decode("utf-8"), stderr.decode("utf-8"))
    return stdout, stderr
