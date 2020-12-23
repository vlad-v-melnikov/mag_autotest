from glob import glob
import os
import argparse


def main():
    reports, logs = parse_arguments()
    if (not reports and not logs) or (reports and logs):
        clear('reports')
        clear('logs')
    elif reports:
        clear('reports')
    elif logs:
        clear('logs')


def clear(what):
    files = glob(f'./{what}/*.log')
    for f in files:
        os.unlink(f)
    if len(files) > 0:
        print(f"Deleted {len(files)} {what}, {what} folder is now empty.")
    else:
        print(f"No {what} to delete")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--reports',
                        help="Indicates that reports need to be deleted.",
                        action="store_true")
    parser.add_argument('-l', '--logs',
                        help="Indicates that logs need to be deleted",
                        action="store_true")

    args = parser.parse_args()

    return args.reports, args.logs


if __name__ == '__main__':
    main()
