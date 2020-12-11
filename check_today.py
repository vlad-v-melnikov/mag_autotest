from modules.wrapper import Wrapper
from modules.today_checker import TodayChecker
import argparse
import traceback


def check_today():
    print(f"Checking if today cycles are present on test...")

    headless, remote, name, password = parse_arguments()
    wrapper = Wrapper('GFS',
                      clear=False,
                      headless=headless,
                      filename='yaml/settings_check_today.yaml',
                      log_name='check_today',
                      remote=remote,
                      name=name,
                      password=password,
                      test_name='Checking availability of today cycles on test')
    cycle_matcher = TodayChecker(driver=wrapper.driver, handles=wrapper.handles, start_time=wrapper.start_time)
    try:
        cycle_matcher.check_today_now()
    except Exception as e:
        print("\n--Something went wrong:--")
        print(e)
        print()
        traceback.print_exc()
    finally:
        wrapper.tear_down()


def parse_arguments():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-l', '--headless',
                       help="Force headless mode irrespective of the settings file",
                       action="store_true")
    group.add_argument('-r', '--remote',
                       nargs=2,
                       help="Remote server testing on BrowserStack, followed by <name> and <password>")

    args = parser.parse_args()
    headless = args.headless
    remote = args.remote is not None
    name = args.remote[0] if remote else ''
    password = args.remote[1] if remote else ''

    return headless, remote, name, password


if __name__ == "__main__":
    check_today()
