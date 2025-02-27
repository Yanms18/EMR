import os
import pip._vendor.requests as requests 
import json

XPC_API_KEY = os.environ.get("XPC_API_KEY")

XPC_FHIR_API_BASE_URL = os.environ.get("XPC_FHIR_API_BASE_URL")
url = XPC_FHIR_API_BASE_URL.rstrip('/') + '/core/api/notes/v1/Note'

headers = {
    'Authorization': f'Bearer {XPC_API_KEY}',
    'Content-Type': 'application/json'
}


def create_note():
  payload = json.dumps({
      "title": "Some Custom Title",
      "noteTypeName": "Office visit",
      "patientKey": "b9d03a4edc0348caa6c030a259caa4ce",
      "providerKey": "9b31de0f2040478e94e4f9b9b409bce0",
      "practiceLocationKey": "d1eacdb5-9ead-47ce-855a-c8c6ef3932a6",
      "encounterStartTime": "2025-02-03T19:00:00.016852Z"
  })

  return requests.request("POST", url, headers=headers, data=payload)
