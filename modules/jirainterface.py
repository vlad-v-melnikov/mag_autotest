import datetime
import time
import requests
import json
from datetime import datetime
# from modules.settings_jira import SettingsJira
from settings_jira import SettingsJira
import sys
from pprint import pprint

class JiraInterface:
    def __init__(self, environment):
        self.settings = SettingsJira(environment)

    def send_report_check_today(self, result, test_case_key, comment, start_time):
        url = f"https://nco-jira.ncep.noaa.gov/rest/atm/1.0/testrun/{self.settings.check_today['cycle_key']}/testcase/{test_case_key}/testresult"
        payload = {
            "status": result,
            "environment": self.settings.environment,
            "actualEndDate": get_now_datetime_utc(),
            "executionTime": (time.time() - start_time) * 1000,
            "scriptResults": [
                {
                    "index": 0,
                    "status": result,
                    "comment": comment
                }
            ]
        }

        with open(self.settings.token_file) as file:
            token = file.read()
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Basic {token}',
            'Cookie': 'JSESSIONID=B6668DF5DA8A0D8B5825AEDD27823258; atlassian.xsrf.token=BZYC-SHM8-8S0W-Z5IJ_1161eb542607d58ae1ad29b0f67da98b39e40fb4_lin'
        }
        requests.request("POST", url, headers=headers, data=json.dumps(payload))

    def create_testcase_for_diff(self):
        url = "https://nco-jira.ncep.noaa.gov/rest/atm/1.0/testcase"
        payload = {
            "projectKey": self.settings.project_key,
            "name": f"Image Diff {get_now_datetime()}",
            "priority": "Normal",
            "status": "Approved",
            "folder": self.settings.compare['folder']
        }

        with open(self.settings.token_file) as file:
            token = file.read()

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json',
            'Cookie': 'JSESSIONID=B6668DF5DA8A0D8B5825AEDD27823258; atlassian.xsrf.token=BZYC-SHM8-8S0W-Z5IJ_1161eb542607d58ae1ad29b0f67da98b39e40fb4_lin'
        }

        result = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        if result.ok:
            return result.json()['key']
        return False

    def add_testcase_steps_for_images(self, test_case, images):
        url = f"https://api.adaptavist.io/tm4j/v2/testcases/{test_case}/teststeps"
        payload = {
            "mode": "OVERWRITE",
            "items": []
        }

        for image in images:
            payload["items"].append(
                {
                    "inline": {
                        "description": f"Test image {image}",
                        "expectedResult": "Image on TEST matches image on PROD"
                    }
                }
            )

        with open(self.settings.token_file) as file:
            token = file.read()
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        return requests.request("POST", url, headers=headers, data=json.dumps(payload))

    def send_execution_image_diff(self, test_case, results):
        url = "https://api.adaptavist.io/tm4j/v2/testexecutions"
        test_script_results = []
        for result in results:
            test_script_results.append(
                {
                    "statusName": f"{result}",
                    "actualEndDate": get_now_datetime_utc(),
                    "actualResult": "TEST matches PROD" if result == 'Pass' else "TEST does not match PROD"
                }
            )
        payload = {
            "projectKey": self.settings.project_key,
            "testCycleKey": self.settings.compare['cycle_key'],
            "testCaseKey": f"{test_case}",
            "statusName": "Pass" if "Fail" not in results else "Fail",
            "testScriptResults": test_script_results,
            "environmentName": self.settings.environment,
            "actualEndDate": get_now_datetime_utc()
        }

        with open(self.settings.token_file) as file:
            token = file.read()
        headers = {
            'Accept': 'application/json',
            'Authorization': f'{token}',
            'Content-Type': 'application/json'
        }

        requests.request("POST", url, headers=headers, data=json.dumps(payload))

    def report_diff_failure(self, test_case, comment):
        # step creation
        url = f"https://nco-jira.ncep.noaa.gov/rest/atm/1.0/testcase/{test_case}"
        payload = {
            "testScript": {
                "type": "STEP_BY_STEP",
                "steps": [
                    {
                        "description": "Test availability of images for diff",
                        "expectedResult": "Images are available for diff"
                    }
                ]
            }
        }

        headers = get_headers(self.get_token())
        requests.request("PUT", url, headers=headers, data=json.dumps(payload))

        # execution
        url = f"https://nco-jira.ncep.noaa.gov/rest/atm/1.0/testrun/{self.settings.compare['cycle_key']}/testcase/{test_case}/testresult"
        test_script_results = [
            {
                "index": 0,
                "status": "Fail",
                "comment": comment
            }
        ]
        payload = {
            "status": "Fail",
            "scriptResults": test_script_results,
            "environment": self.settings.environment,
            "actualEndDate": get_now_datetime_utc()
        }

        headers = get_headers(self.get_token())
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        print(response.json())


    def get_token(self):
        with open(self.settings.token_file) as file:
            token = file.read()
        return token


def get_now_datetime_utc():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def get_now_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_headers(token):
    return {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Basic {token}',
            'Cookie': 'JSESSIONID=B6668DF5DA8A0D8B5825AEDD27823258; atlassian.xsrf.token=BZYC-SHM8-8S0W-Z5IJ_1161eb542607d58ae1ad29b0f67da98b39e40fb4_lin'
        }


if __name__ == '__main__':
    jira = JiraInterface('Firefox')
    jira.report_diff_failure('MAG-T29', 'No images for diff found')
