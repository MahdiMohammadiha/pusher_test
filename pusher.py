import os
import subprocess
import time
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL")
TIME_PERIOD = 10
LOG_FILE = "out.log"

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.decode().strip(), None
    except subprocess.CalledProcessError as e:
        return None, e.stderr.decode().strip()

def log_message(message):
    """Log a message to the log file with timestamp."""
    with open(LOG_FILE, "a") as log_file:
        timestamp = datetime.now(pytz.timezone("Asia/Tehran")).strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} - {message}\n")

def initialize_git_repo():
    """Initialize a new Git repository if it doesn't exist."""
    print("Initializing a new Git repository...")
    run_command("git init")
    run_command('git commit --allow-empty -m "Initial commit"')
    run_command("git branch -M main")
    print("Done.")

def pull_latest_changes(origin):
    """Pull the latest changes from the remote repository."""
    print("Pulling latest changes from remote repository...")
    stdout, stderr = run_command(f"git pull --rebase {origin} main")
    if stderr:
        print("Error pulling changes.")
        print("Beginning automatic force push sequence...")
        shall_run = input("For start [s] and anything else for stop sequence: ")
        if shall_run.lower() == "s":
            run_command("git add .")
            run_command('git commit -m "Automated commit | FORCE PUSH"')
            run_command(f"git push {origin} main -f")
            print("Force push successful.")
            return True
        else:
            print("Operation canceled.")
            return False
    else:
        print("Done.")
        return True

def perform_git_operations(origin):
    """Perform the main git operations."""
    print(f"Pusher is running (time period is {TIME_PERIOD}s)...")
    print(f"Check '{LOG_FILE}' for logging status.")

    while True:
        try:
            # Get current date and time in Iran timezone
            iran_tz = pytz.timezone("Asia/Tehran")
            current_time = datetime.now(iran_tz).strftime("%Y-%m-%d %H:%M:%S")

            # Create commit message
            commit_message = f"Automated commit | {current_time}"

            # Add the files to the Git repository
            stdout, stderr = run_command("git add .")
            if stderr:
                log_message(f"Error adding files: {stderr}")

            # Check if there are changes to commit
            stdout, stderr = run_command("git status --porcelain")
            if stdout:  # If there is output, there are changes
                stdout, stderr = run_command(f'git commit -m "{commit_message}"')
                if stderr:
                    log_message(f"Error committing changes: {stderr}")

                # Push the changes to a remote GitHub repository
                stdout, stderr = run_command(f"git push {origin} main")
                if stderr:
                    log_message(f"Error pushing changes: {stderr}")
                else:
                    log_message("Push successful.")
            else:
                log_message("No changes to commit.")

        except Exception as e:
            log_message(f"An error occurred: {e}")

        # Wait for the next push period
        time.sleep(TIME_PERIOD)

def main():
    """Main function to run the script."""
    origin = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@{GITHUB_REPO_URL}"
    
    if not os.path.exists(os.path.join(os.getcwd(), ".git")):
        initialize_git_repo()
    else:
        print("A Git repository already exists in this directory.")

    pull_status = pull_latest_changes(origin)
    if pull_status:
        try:
            perform_git_operations(origin)
        except KeyboardInterrupt:
            print("\nOperation canceled.")

if __name__ == "__main__":
    main()
