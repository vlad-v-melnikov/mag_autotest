import yaml
from pprint import pprint


class Settings:
    def __init__(self, filename='yaml/settings_default.yaml'):

        with open(filename) as file:
            self.settings = yaml.load(file, Loader=yaml.FullLoader)

        self.filename = filename
        self.sites = self.settings['sites']
        self.driver = self.settings['driver']
        self.headless = self.settings['headless']
        self.remote = self.settings['remote']
        self.plan = self.settings['plan']
        self.delays = self.settings['delays']


def main():
    settings = Settings()

    pprint(settings.sites)
    pprint(settings.driver)
    pprint(settings.plan)
    pprint(settings.remote)


if __name__ == "__main__":
    main()
