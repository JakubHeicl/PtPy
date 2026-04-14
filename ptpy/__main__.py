from pathlib import Path

from .engine import run, show_status, restore
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--status", action="store_true", help="Show status of all cases in the repository.")
parser.add_argument("--restore", action="store_true", help="Restore the workflow from the repository and cancel all running jobs. Use with caution as this will remove the repository and all run folders.")
parser.add_argument("--do-not-ask", action="store_true", help="Do not ask for confirmation when starting new jobs or when restoring the workflow. Use with caution as this may lead to unintended consequences.")
parser.add_argument("--log-file", type=Path, default=None, help="Path to the log file.")
parser.add_argument("--loop", action="store_true", help="Run the workflow in a loop, checking for new cases and running jobs every few seconds.")

if __name__ == "__main__":
    args = parser.parse_args()
    if args.status:
        show_status(verbose = not args.do_not_ask, log_file=args.log_file)
    elif args.restore:
        restore(verbose = not args.do_not_ask, log_file=args.log_file)
    else:
        run(verbose = not args.do_not_ask, log_file=args.log_file, loop=args.loop)