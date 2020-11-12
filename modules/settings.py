import json
from pprint import pprint


class Settings:
    def __init__(self, filename='json/settings_default.json'):

        with open(filename) as json_file:
            self.settings = json.load(json_file)

        self.filename = filename
        self.sites = self.settings['sites']
        self.driver = self.settings['driver']
        self.headless = self.settings['headless']
        self.plan = self.settings['plan']
        self.delays = self.settings['delays']

    def save(self):
        all_settings = {
            'sites': self.sites,
            'driver': self.driver,
            'headless': self.headless,
            'plan': self.plan,
            'delays': self.delays
        }
        with open(self.filename, 'w') as json_file:
            json.dump(all_settings, json_file, indent=2)


def main():
    settings = Settings()

    pprint(settings.sites)
    pprint(settings.driver)
    pprint(settings.plan)


if __name__ == "__main__":
    main()
