from modules.wrapper import Wrapper
from modules.today_checker import TodayChecker
from time import time


def check_today():
    start_time = time()
    print(f"Checking if today cycles are present on test...")

    wrapper = Wrapper('GFS', clear=False)
    cycle_matcher = TodayChecker(driver=wrapper.driver, handles=wrapper.handles)

    cycle_matcher.check_today_now()
    wrapper.tear_down()
    print(f"\nDone checking cycles. Running time: {(time() - start_time):.2f} seconds")


if __name__ == "__main__":
    check_today()

# To Do:
#
