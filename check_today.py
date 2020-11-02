from modules.wrapper import Wrapper
from modules.gfs_like import GfsLike
from modules.sref_cluster import SREFCluster
from modules.panels import Panels
from modules.storm_tracks import StormTracks
from modules.cycle_matcher import CycleMatcher


def check_today():
    print(f"Checking if today cycles are present on test...")
    wrapper = Wrapper()
    cycle_matcher = CycleMatcher(driver=wrapper.driver, handles=wrapper.handles)
    cycle_matcher.check_today_now()
    wrapper.tear_down()
    print("\nDone checking cycles")


if __name__ == "__main__":
    check_today()

# To Do:
#
