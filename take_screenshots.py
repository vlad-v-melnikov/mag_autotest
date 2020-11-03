from modules.wrapper import Wrapper
from modules.gfs_like import GfsLike
from modules.sref_cluster import SREFCluster
from modules.panels import Panels
from modules.storm_tracks import StormTracks
import argparse

CLASS_MAP = {
        'PANELS': Panels,
        'SREF-CLUSTER': SREFCluster,
        'STORM-TRACKS': StormTracks,
    }


def take_screenshots():
    parser = argparse.ArgumentParser()
    parser.add_argument('model',
                        help="Model name to take screenshots")
    parser.add_argument('-s', '--settings',
                        help="Name of the json settings file different from default_settings.json")
    args = parser.parse_args()
    model = args.model
    filename = args.settings if args.settings else 'settings_default.json'

    print(f"Screenshots for {model}.")
    wrapper = Wrapper(model=model, filename=filename)

    if model in CLASS_MAP.keys():
        single_model = CLASS_MAP[model](model=model, driver=wrapper.driver, handles=wrapper.handles, filename=filename)
    else:
        single_model = GfsLike(model=model, driver=wrapper.driver, handles=wrapper.handles, filename=filename)

    single_model.make_now()

    wrapper.tear_down()
    print("Screenshots taken.")


if __name__ == "__main__":
    take_screenshots()
