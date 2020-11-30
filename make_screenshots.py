from modules.wrapper import Wrapper
from modules.settings import Settings
from modules.gfs_like import GfsLike
from modules.sref_cluster import SREFCluster
from modules.panels import Panels
from modules.storm_tracks import StormTracks
from modules.uair import Uair
from modules.skewt import Skewt
from modules.trop import Trop
from modules.soundings import Soundings
import argparse
import traceback


CLASS_MAP = {
        'PANELS': Panels,
        'SREF-CLUSTER': SREFCluster,
        'STORM-TRACKS': StormTracks,
        'UAIR': Uair,
        'RTMA': Uair,
        'SKEWT': Skewt,
        'TROP': Trop,
        'GFS-SND': Soundings,
        'NAM-SND': Soundings,
    }


def take_screenshots():
    model, filename, headless = parse_arguments()
    print(f"Screenshots for {model}.")
    wrapper = Wrapper(model=model, filename=filename, headless=headless)

    if model in CLASS_MAP.keys():
        single_model = CLASS_MAP[model](model=model, driver=wrapper.driver, handles=wrapper.handles, filename=filename)
    else:
        single_model = GfsLike(model=model, driver=wrapper.driver, handles=wrapper.handles, filename=filename)

    try:
        single_model.make_now()
    except Exception as e:
        print("\n--Something went wrong:--")
        print(e)
        print()
        traceback.print_exc()
    finally:
        wrapper.tear_down()


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('model',
                        help="Model name to take screenshots")
    parser.add_argument('-s', '--settings',
                        help="Name of the yaml settings file different from default_settings.yaml")
    parser.add_argument('-l', '--headless',
                        help="Force headless mode irrespective of the settings file",
                        action="store_true")

    args = parser.parse_args()
    model = args.model.upper()
    headless = args.headless

    filename = args.settings if args.settings else 'yaml/settings_default.yaml'
    if filename[:5] != 'yaml/':
        filename = 'yaml/' + filename

    return model, filename, headless


if __name__ == "__main__":
    take_screenshots()
