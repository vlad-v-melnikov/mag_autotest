import datetime
import time
import requests
import json
from datetime import datetime
from modules.settings_jira import SettingsJira
import sys

TODAY_TESTCASES = {
    'GFS': 'MT-T3',
    'GEFS-SPAG': 'MT-T4',
    'NAEFS': 'MT-T5',
    'NAM': 'MT-T6',
    'NAM-HIRES': 'MT-T7',
    'FIREWX': 'MT-T8',
    'RAP': 'MT-T9',
    'HRRR': 'MT-T10',
    'HRW-NMMB': 'MT-T11',
    'HRW-ARW': 'MT-T12',
    'HRW-ARW2': 'MT-T13',
    'SREF': 'MT-T14',
    'HREF': 'MT-T15',
    'NBM': 'MT-T16',
    'SREF-CLUSTER': 'MT-T17',
    'WW3': 'MT-T18',
    'ESTOFS': 'MT-T19',
    'ICE-DRIFT': 'MT-T20',
    'STORM-TRACKS': 'MT-T21',
    'UAIR': 'MT-T22',
    'SKEWT': 'MT-T23',
    'RTMA': 'MT-T24',
    'TROP': 'MT-T25',
    'GFS-SND': 'MT-T26',
    'NAM-SND': 'MT-T27'
}


class JiraInterface:
    def __init__(self, environment):
        self.settings = SettingsJira(environment)

    def send_report_check_today(self, result, test_case_key, comment, start_time):
        url = "https://api.adaptavist.io/tm4j/v2/testexecutions"
        payload = {
            "projectKey": self.settings.project_key,
            "testCycleKey": self.settings.check_today['cycle_key'],
            "testCaseKey": test_case_key,
            "statusName": result,
            "environmentName": self.settings.environment,
            "actualEndDate": get_now_datetime_utc(),
            "executionTime": (time.time() - start_time) * 1000,
            "testScriptResults": [
                {
                    "statusName": result,
                    "actualEndDate": get_now_datetime_utc(),
                    "actualResult": comment
                }
            ],
        }

        with open(self.settings.token_file) as file:
            token = file.read()
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        requests.request("POST", url, headers=headers, data=json.dumps(payload))

    def create_testcase_for_diff(self):
        url = "https://api.adaptavist.io/tm4j/v2/testcases"
        payload = {
            "projectKey": self.settings.project_key,
            "name": f"Image Diff {get_now_datetime()}",
            "priorityName": "Normal",
            "statusName": "Approved",
            "folderId": self.settings.compare['folder_id']
        }

        with open(self.settings.token_file) as file:
            token = file.read()

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        result = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        if "errorCode" not in result.json():
            return result.json()["key"]
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
        url = f"https://api.adaptavist.io/tm4j/v2/testcases/{test_case}/teststeps"
        payload = {
            "mode": "OVERWRITE",
            "items": []
        }

        payload["items"].append(
            {
                "inline": {
                    "description": f"Test availability of images for diff",
                    "expectedResult": "Images are available for diff"
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

        requests.request("POST", url, headers=headers, data=json.dumps(payload))

        #execution
        url = "https://api.adaptavist.io/tm4j/v2/testexecutions"
        testScriptResults = [
            {
                "statusName": "Fail",
                "actualEndDate": get_now_datetime_utc(),
                "actualResult": comment
            }
        ]
        payload = {
            "projectKey": self.settings.project_key,
            "testCycleKey": self.settings.compare['cycle_key'],
            "testCaseKey": f"{test_case}",
            "statusName": "Fail",
            "testScriptResults": testScriptResults,
            "environmentName": self.settings.environment,
            "actualEndDate": get_now_datetime_utc()
        }

        headers = {
            'Accept': 'application/json',
            'Authorization': f'{token}',
            'Content-Type': 'application/json'
        }

        requests.request("POST", url, headers=headers, data=json.dumps(payload))


def get_now_datetime_utc():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def get_now_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == '__main__':
    jira = JiraInterface('Firefox')
    test_case = jira.create_testcase_for_diff()
    if not test_case:
        sys.exit(0)
    jira.report_diff_failure(test_case, 'Did not find any images')

