import requests
from datetime import date

def age_to_iso_birthday_fixed(age):
    year = date.today().year - age
    approx_birthday = date(year, 1, 1)  # Always January 1
    return approx_birthday.isoformat()

def create_patient0(firstname, lastname, age, sex):
    payload = {
        "resourceType": "Patient",
        "extension": [
            {
                "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex",
                "valueCode": sex
            }
        ],
        "gender": sex,
        "active": True,
        "name": [
            {
                "use": "official",
                "family": lastname,
                "given": [
                    firstname
                ]
            }
        ],
        "birthDate": age_to_iso_birthday_fixed(age)
    }
    return payload
