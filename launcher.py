import glob
import logging
import os
from retry import retry
import time

# selenium
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from datetime import datetime

# internal
from settings import Settings
from wrapper import Wrapper
from gfs_like import GfsLike
from sref_cluster import SREFCluster
from panels import Panels
from storm_tracks import StormTracks

CLASS_MAP = {
        'PANELS': Panels,
        'SREF-CLUSTER': SREFCluster,
        'STORM-TRACKS': StormTracks,
    }


def screenshots_main():
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

def cycle_match_checker_main():
    pass

if __name__ == "__main__":
    screenshots_main()

# To Do:
#
