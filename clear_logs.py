from glob import glob
import os


def clear_screenshots():
    files = glob(f'./logs/*.log')
    for f in files:
        os.unlink(f)
    if len(files) > 0:
        print(f"Deleted {len(files)} logs. Log folder is now empty.")


if __name__ == '__main__':
    clear_screenshots()