from .engine import run, show_status, run_test
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--status", action="store_true", help="Show status of all cases in the repository.")
parser.add_argument("--test", action="store_true", help="Run test")

if __name__ == "__main__":
    args = parser.parse_args()
    if args.status:
        show_status()
    elif args.test:
        run_test()
    else:
        run()