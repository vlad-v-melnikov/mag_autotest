from glob import glob
import os
import argparse


def clear_screenshots():
    model = parse_arguments()
    files = glob(f'./screenshots/*{model}*.png') if model else glob(f'./screenshots/*.png')
    for f in files:
        os.unlink(f)
    if len(files) > 0:
        print(f"Deleted {len(files)} files.")
    else:
        print("No files to delete.")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model',
                        help="Model name which screenshots should be removed")
    args = parser.parse_args()
    return args.model.upper()


if __name__ == '__main__':
    clear_screenshots()
