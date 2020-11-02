from modules.wrapper import Wrapper
from modules.gfs_like import GfsLike
from modules.sref_cluster import SREFCluster
from modules.panels import Panels
from modules.storm_tracks import StormTracks
from modules.cycle_matcher import CycleMatcher
import sys
import argparse

CLASS_MAP = {
        'PANELS': Panels,
        'SREF-CLUSTER': SREFCluster,
        'STORM-TRACKS': StormTracks,
    }


def take_screenshots():
    parser = argparse.ArgumentParser()
    parser.add_argument('model', help="Model name to take screenshots")
    args = parser.parse_args()
    model = args.model

    print(f"Screenshots for {model}.")
    wrapper = Wrapper()

    if model in CLASS_MAP.keys():
        single_model = CLASS_MAP[model](model=model, driver=wrapper.driver, handles=wrapper.handles)
    else:
        single_model = GfsLike(model=model, driver=wrapper.driver, handles=wrapper.handles)

    single_model.make_now()

    wrapper.tear_down()
    print("Screenshots taken.")


if __name__ == "__main__":
    take_screenshots()
