from glob import glob
import os


def clear_screenshots():
    files = glob(f'./screenshots/*.png')
    for f in files:
        os.unlink(f)
    if len(files) > 0:
        print("Screenshot folder is now empty.")


if __name__ == '__main__':
    clear_screenshots()
