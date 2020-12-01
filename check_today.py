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
                      password=password)
    cycle_matcher = TodayChecker(driver=wrapper.driver, handles=wrapper.handles)
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
    parser.add_argument('-l', '--headless',
                        help="Force headless mode irrespective of the settings file",
                        action="store_true")
    parser.add_argument('-r', '--remote',
                        help="Remote server testing on BrowserStack",
                        action="store_true")
    parser.add_argument('-n', '--name',
                        help="Name for remote access to BrowserStack")
    parser.add_argument('-p', '--pwd',
                        help="Password for remote access to BrowserStack")
    args = parser.parse_args()
    headless = args.headless
    remote = args.remote
    name = args.name
    pwd = args.pwd

    return headless, remote, name, pwd


if __name__ == "__main__":
    check_today()
