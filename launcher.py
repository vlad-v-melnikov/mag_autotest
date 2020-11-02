from modules.wrapper import Wrapper
from modules.gfs_like import GfsLike
from modules.sref_cluster import SREFCluster
from modules.panels import Panels
from modules.storm_tracks import StormTracks
from modules.cycle_matcher import CycleMatcher

CLASS_MAP = {
        'PANELS': Panels,
        'SREF-CLUSTER': SREFCluster,
        'STORM-TRACKS': StormTracks,
    }


def take_screenshots():
    model = 'ICE-DRIFT'

    print(f"Starting to take screenshots for {model}...")
    wrapper = Wrapper()

    if model in CLASS_MAP.keys():
        single_model = CLASS_MAP[model](model=model, driver=wrapper.driver, handles=wrapper.handles)
    else:
        single_model = GfsLike(model=model, driver=wrapper.driver, handles=wrapper.handles)

    single_model.make_now()

    wrapper.tear_down()
    print("\nScreenshots taken")


def match_cycles():
    print(f"Starting to match cycles for test and prod...")
    wrapper = Wrapper()
    cycle_matcher = CycleMatcher(driver=wrapper.driver, handles=wrapper.handles)
    cycle_matcher.match_now()
    wrapper.tear_down()
    print("\nDone matching cycles")


if __name__ == "__main__":
    match_cycles()

# To Do:
#
