import yaml
from pprint import pprint
import requests


class SettingsJira:
    def __init__(self, environment, filename='yaml/settings_jira.yaml'):

        with open(filename) as file:
            self.settings = yaml.load(file, Loader=yaml.FullLoader)

        self.project_key = self.settings['project_key']
        self.token_file = self.settings['token_file']
        self.compare = self.settings['compare']
        self.check_today = self.settings['check_today']

        if environment in self.get_environments():
            self.environment = environment
        else:
            self.environment = 'Unknown'

    def get_environments(self):
        url = "https://api.adaptavist.io/tm4j/v2/environments"
        with open(self.token_file) as file:
            token = file.read()
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        response = requests.request("GET", url, headers=headers).json()
        environments = []
        for val in response['values']:
            environments.append(val['name'])

        return environments


def main():
    settings = SettingsJira('IE')
    print(settings.project_key, settings.token_file, settings.environment, sep='\n')
    pprint(settings.compare)
    pprint(settings.check_today)


if __name__ == "__main__":
    main()
