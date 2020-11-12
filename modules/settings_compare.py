import json
from pprint import pprint


class SettingsCompare:
    def __init__(self, filename='json/settings_compare.json'):

        with open(filename) as json_file:
            self.settings = json.load(json_file)

        self.compare = self.settings['compare']
        self.driver = self.settings['driver']


def main():
    settings = SettingsCompare()
    pprint(settings.compare)


if __name__ == "__main__":
    main()
