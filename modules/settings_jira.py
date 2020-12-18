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
        self.TODAY_TESTCASES = self.settings['TODAY_TESTCASES']

        if environment in self.get_environments(self.settings['project_key']):
            self.environment = environment
        else:
            self.environment = 'Unknown'

    def get_environments(self, project_key):
        url = f"https://nco-jira.ncep.noaa.gov/rest/atm/1.0/environments?projectKey={project_key}"
        with open(self.token_file) as file:
            token = file.read()
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Basic {token}',
            'Cookie': 'JSESSIONID=B6668DF5DA8A0D8B5825AEDD27823258; '
                      'atlassian.xsrf.token=BZYC-SHM8-8S0W-Z5IJ_1161eb542607d58ae1ad29b0f67da98b39e40fb4_lin'
        }

        response = requests.request("GET", url, headers=headers).json()
        environments = []
        for val in response:
            environments.append(val['name'])

        return environments


def main():
    settings = SettingsJira('Firefox')
    print(settings.project_key, settings.token_file, settings.environment, sep='\n')
    pprint(settings.compare)
    pprint(settings.check_today)


if __name__ == "__main__":
    main()
