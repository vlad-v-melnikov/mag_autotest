import yaml
from pprint import pprint
import requests
import sys
import json

class SettingsJira:
    def __init__(self, environment='Unknown', filename='yaml/settings_jira.yaml'):

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
        try:
            with open(self.token_file) as file:
                token = file.read()
        except FileNotFoundError:
            print(f'---Could not send info to Jira. Token file "{self.token_file}" is not found.---')
            sys.exit(0)
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Basic {token}',
            'Cookie': 'JSESSIONID=B6668DF5DA8A0D8B5825AEDD27823258; '
                      'atlassian.xsrf.token=BZYC-SHM8-8S0W-Z5IJ_1161eb542607d58ae1ad29b0f67da98b39e40fb4_lin'
        }

        try:
            response = requests.request("GET", url, headers=headers)
        except Exception as e:
            print('\n', type(e), '\n', e, '\n')
            print('---Could not connect to Jira: check VPN and/or connection parameters---')
            sys.exit(0)

        try:
            response_json = response.json()
        except json.JSONDecodeError:
            print("---Could not connect to Jira:---")
            print("Response error code:", response.status_code)
            if response.status_code == 401 or response.status_code == 403:
                print("Authentication error: make your token again with correct username and password")
                if response.status_code == 403:
                    print("If this error repeats, you may need to enter Jira from your browser and enter CAPTCHA.")
            else:
                print(response.text)
            sys.exit(0)

        environments = []
        for val in response_json:
            environments.append(val['name'])

        return environments


def main():
    settings = SettingsJira('Firefox')
    print(settings.project_key, settings.token_file, settings.environment, sep='\n')
    pprint(settings.compare)
    pprint(settings.check_today)


if __name__ == "__main__":
    main()
