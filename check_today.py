from modules.wrapper import Wrapper
from modules.today_checker import TodayChecker
from time import time
import argparse


def check_today():
    start_time = time()
    print(f"Checking if today cycles are present on test...")

    wrapper = Wrapper('GFS', clear=False, headless=parse_arguments())
    cycle_matcher = TodayChecker(driver=wrapper.driver, handles=wrapper.handles)

    cycle_matcher.check_today_now()
    wrapper.tear_down()
    print(f"\nDone checking cycles. Running time: {(time() - start_time):.2f} seconds")


def parse_arguments() -> bool:
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--headless',
                        help="Force headless mode irrespective of the settings file",
                        action="store_true")
    args = parser.parse_args()
    headless = args.headless
    return headless


if __name__ == "__main__":
    check_today()

# To Do:
#
