import subprocess
from datetime import datetime

class GitManager:

    def __init__(self, repo_path="."): # . means current folder
        self.repo_path = repo_path

    def auto_commit(self, message="Pipeline run"):
        try:
            # add all changes
            subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True) #qovluqdaki butun deyisiklikleri goturur

            # timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_message = f"{message} | {timestamp}"

            # commit
            subprocess.run(
                ["git", "commit", "-m", full_message],
                cwd=self.repo_path,
                check=True
            )

            print(" Git commit done")

        except Exception as e:  #hec bir deyisiklik olmadiqda ekrana git commit erroru verir, amma kod islemeye davam edir.
            print(" Git commit skipped or failed:", e)