import yaml
from pprint import pprint


class SettingsCompare:
    def __init__(self, filename='yaml/settings_compare.yaml'):

        with open(filename) as file:
            self.settings = yaml.load(file, Loader=yaml.FullLoader)

        self.compare = self.settings['compare']
        self.driver = self.settings['driver']


def main():
    settings = SettingsCompare()
    pprint(settings.compare)


if __name__ == "__main__":
    main()
