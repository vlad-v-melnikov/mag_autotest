from modules.wrapper import Wrapper
from modules.today_checker import TodayChecker


def check_today():
    print(f"Checking if today cycles are present on test...")

    wrapper = Wrapper('GFS', clear=False)
    cycle_matcher = TodayChecker(driver=wrapper.driver, handles=wrapper.handles)

    cycle_matcher.check_today_now()
    wrapper.tear_down()
    print("Done checking cycles")


if __name__ == "__main__":
    check_today()

# To Do:
#
