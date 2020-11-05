import json
from pprint import pprint


class Settings:
    def __init__(self, filename='settings_default.json'):

        with open(filename) as json_file:
            self.settings = json.load(json_file)

        self.sites = self.settings['sites']
        self.driver = self.settings['driver']
        self.headless = self.settings['headless']
        self.plan = self.settings['plan']
        self.compare = self.settings['compare']


def main():
    settings = Settings()

    pprint(settings.sites)
    pprint(settings.driver)
    pprint(settings.compare)
    pprint(settings.plan)


if __name__ == "__main__":
    main()
