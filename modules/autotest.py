import datetime
import time
import requests
import json
from datetime import datetime

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


def send_report(result, cycle_key, test_case_key, comment, start_time):
    url = "https://api.adaptavist.io/tm4j/v2/testexecutions"
    payload = {
        "projectKey": "MT",
        "testCycleKey": cycle_key,
        "testCaseKey": test_case_key,
        "statusName": result,
        "environmentName": "Firefox",
        "actualEndDate": get_now_datetime(),
        "executionTime": (time.time() - start_time) * 1000,
        "testScriptResults": [
            {
                "statusName": result,
                "actualEndDate": get_now_datetime(),
                "actualResult": comment
            }
        ],
    }

    # print("Payload:")
    # print(payload)

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMDdhN2M5Zi01Y2EyLTM5MmEtYmJiNi0wOGJhNGYxNDdjOWUiLCJjb250ZXh0Ijp7ImJhc2VVcmwiOiJodHRwczpcL1wvdm1lbG5pa292LmF0bGFzc2lhbi5uZXQiLCJ1c2VyIjp7ImFjY291bnRJZCI6IjViOGRkYzU2OGFhYTBmMmJkMTFmYTM1NiJ9fSwiaXNzIjoiY29tLmthbm9haC50ZXN0LW1hbmFnZXIiLCJleHAiOjE2MzkwNzMwNjksImlhdCI6MTYwNzUzNzA2OX0.IyGN1eAX9s_T7B5eFJ91okpihQncinijH6Mc5eAadj4',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    # print(response.text)


def get_now_datetime():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
