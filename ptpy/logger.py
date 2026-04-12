from pathlib import Path

class Logger:
    def __init__(self, verbose: bool = True, log_file: Path | None = None):
        self.verbose = verbose
        self.log_file = log_file

    def log(self, message: str):
        print(message)

        if self.log_file is not None:
            with open(self.log_file, "a") as f:
                f.write(message + "\n")

    def reassure(self, question: str) -> bool:
        if not self.verbose:
            return True
        
        return input(question + " (y/n): ").lower() == "y"